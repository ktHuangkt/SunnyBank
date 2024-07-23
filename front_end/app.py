from flask import Flask, render_template
# import report_generator

app = Flask(__name__,
            template_folder='C:/Users/User/Downloads/training_syscom/training_syscom',
            static_folder='C:/Users/User/Downloads/training_syscom/training_syscom')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/market')
def market_report():
    return render_template('market.html')
    # return render_template('market.html', report=report_generator.response_text)

@app.route('/investment')
def investment():
    return render_template('investment.html')

@app.route('/product')
def product():
    return render_template('product.html')

if __name__ == '__main__':
    app.run(debug=True)
