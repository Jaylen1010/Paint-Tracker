from flask import Flask, render_template, request, redirect, url_for
from backend import get_all_paint_logs, add_paint_log, delete_paint_log, get_totals

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle form submission to add log
        hours = float(request.form['hours'])
        percent = float(request.form['percent'])
        area = float(request.form['area'])
        room = request.form['room'].strip()
        add_paint_log(hours, percent, area, room)
        return redirect(url_for('index'))

    logs = get_all_paint_logs()
    total_percent, total_hours, room_number = get_totals()

    return render_template('home.html',
                           logs=logs,
                           total_percent=total_percent,
                           total_hours=total_hours,
                           total_area=sum(log['area'] for log in logs),
                           room_number=room_number)

@app.route('/delete/<int:numeric_id>')
def delete(numeric_id):
    delete_paint_log(numeric_id)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
