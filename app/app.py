from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DB_USER = os.getenv("DB_USER", "readinglist")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")
DB_NAME = os.getenv("DB_NAME", "readinglist")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    status = Column(String(50), default="unread")  # unread, reading, finished

app = Flask(__name__)

def init_db():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

# Initialize DB at import time (once per process)
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/config")
def config():
    return {
        "banner": os.getenv("BANNER_MESSAGE", ""),
        "env": os.getenv("APP_ENV", "unknown")
    }

@app.route("/healthz")
def health():
    return {"status": "ok"}

@app.route("/books", methods=["GET"])
def list_books():
    session = SessionLocal()
    books = session.query(Book).all()
    data = [
        {"id": b.id, "title": b.title, "author": b.author, "status": b.status}
        for b in books
    ]
    session.close()
    return jsonify(data)

@app.route("/books", methods=["POST"])
def add_book():
    body = request.get_json() or {}
    title = body.get("title")
    author = body.get("author")
    status = body.get("status", "unread")

    if not title or not author:
        return {"error": "title and author are required"}, 400

    session = SessionLocal()
    book = Book(title=title, author=author, status=status)
    session.add(book)
    session.commit()
    result = {"id": book.id, "title": book.title, "author": book.author, "status": book.status}
    session.close()
    return result, 201

@app.route("/books/<int:book_id>", methods=["PATCH"])
def update_book(book_id):
    body = request.get_json() or {}
    session = SessionLocal()
    book = session.query(Book).get(book_id)
    if not book:
        session.close()
        return {"error": "not found"}, 404

    if "title" in body:
        book.title = body["title"]
    if "author" in body:
        book.author = body["author"]
    if "status" in body:
        book.status = body["status"]
    session.commit()
    result = {"id": book.id, "title": book.title, "author": book.author, "status": book.status}
    session.close()
    return result

@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    session = SessionLocal()
    book = session.query(Book).get(book_id)
    if not book:
        session.close()
        return {"error": "not found"}, 404
    session.delete(book)
    session.commit()
    session.close()
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
