from api.v10 import app

HOST='0.0.0.0'
PORT=5112

def main():
    app.run(HOST, PORT, debug=True)
    
if __name__ == "__main__":
    main()