from flask import Flask, render_template
from datetime import datetime
import market_report_generator
import investment_report_generator

app = Flask(__name__,
            template_folder='C:/Users/User/Downloads/training_syscom/training_syscom',
            static_folder='C:/Users/User/Downloads/training_syscom/training_syscom')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/market')
def market():
    # return render_template('market.html')
    today_date = datetime.now().strftime('%Y/%m/%d')  # 獲取當天日期
    return render_template('market.html', 
                           report=market_report_generator.market_report,
                           date=today_date)

@app.route('/investment')
def investment():
    today_date = datetime.now().strftime('%Y/%m/%d')  # 獲取當天日期
    return render_template('investment.html',
                           report=investment_report_generator.investment_report,
                           date=today_date)

@app.route('/product')
def product():
    return render_template('product.html')

if __name__ == '__main__':
    app.run(debug=True)
