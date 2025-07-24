from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime

SERVICE_ACCOUNT_PATH = "creds.json"
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_PATH)
db = firestore.Client(credentials=credentials)

collection_name = "paint_logs"
counter_doc = db.collection("meta").document("log_counter")


def _get_next_log_id():
    """
    Atomically get and increment the log ID counter.
    """
    counter_doc_ref = counter_doc

    @firestore.transactional
    def transaction_update(transaction):
        snapshot = counter_doc_ref.get(transaction=transaction)
        current_id = snapshot.get("value") if snapshot.exists else 0
        next_id = current_id + 1
        transaction.set(counter_doc_ref, {"value": next_id})
        return next_id

    transaction = db.transaction()
    return transaction_update(transaction)



def add_paint_log(hours, percent, area, room):
    numeric_id = _get_next_log_id()
    data = {
        "numeric_id": numeric_id,
        "hours": float(hours),
        "percent": float(percent),
        "area": float(area),
        "room": room,
        "timestamp": datetime.utcnow()
    }
    doc_id = str(numeric_id)
    db.collection(collection_name).document(doc_id).set(data)
    print(f"✅ Added log with numeric ID: {doc_id}")
    return doc_id


def get_all_paint_logs():
    """
    Returns all logs ordered by numeric_id descending,
    with formatted timestamp.
    """
    docs = db.collection(collection_name).order_by("numeric_id", direction=firestore.Query.DESCENDING).stream()
    logs = []
    for doc in docs:
        data = doc.to_dict()
        ts = data.get("timestamp")

        # Format the timestamp if it exists and is a datetime object
        if isinstance(ts, datetime):
            data["formatted_time"] = ts.strftime("%B %d, %Y @ %I:%M %p")
        else:
            data["formatted_time"] = "Unknown"

        data["doc_id"] = doc.id
        logs.append(data)
    return logs



def delete_paint_log(numeric_id):
    doc_id = str(numeric_id)
    db.collection(collection_name).document(doc_id).delete()
    print(f"🗑️ Deleted log with numeric ID: {doc_id}")

def initialize_counter():
    counter_doc.set({"value": 0})
    print("🔧 Initialized log counter to 0")

def get_totals():
    percent = 0
    room_number = 0
    hours = 0
    rooms = []

    for log in get_all_paint_logs():
        percent += log['percent']
        hours += log['hours']
        rooms.append(log['room'])
    
    room_number = len(set(rooms))
    
    return percent, hours, room_number



