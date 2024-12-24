from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")
db = client["expense_tracker"]
transactions = db["transactions"]

# Homepage with transactions
@app.route('/')
def index():
    # Fetch transactions from MongoDB
    all_transactions = list(transactions.find())
    for transaction in all_transactions:
        transaction["_id"] = str(transaction["_id"])  # Convert ObjectId to string for safe use
    
    # Debugging: Print data passed to the template
    print("Transactions passed to HTML:", all_transactions)
    
    return render_template('index.html', transactions=all_transactions)


# Endpoint for uploading Excel file
@app.route('/upload', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        flash("No file uploaded", 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename.endswith('.xlsx'):
        df = pd.read_excel(file)
        
        # Match Excel columns to MongoDB schema
        df.rename(columns={
            "Amount": "amount", 
            "Category": "category", 
            "TransactionDate": "date", 
            "Details": "description"
        }, inplace=True)
        
        # Insert data into MongoDB
        data = df.to_dict('records')  # Convert DataFrame to a list of dictionaries
        transactions.insert_many(data)
        
        flash(f"{len(data)} records uploaded successfully!", 'success')
        return redirect(url_for('index'))
    else:
        flash("Invalid file type. Please upload an Excel file.", 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
