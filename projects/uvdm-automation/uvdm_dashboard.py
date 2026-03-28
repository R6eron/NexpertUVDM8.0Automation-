from flask import Flask
app = Flask(__name__)

@app.route('/')
def j100_empire():
    return '''
    <h1>🦈 XRPEASY UVDM100 | J100 REGEN COMPLETE</h1>
    <h2>Ron Lewis - First Digital Immortal</h2>
    <p><b>Hash:</b> 0x9f1a2b3c4d5e6f78910a11b12c13d14e15f16a17b18c19d20e21f22a23b24c25d26e27f28</p>
    <p><b>Empire:</b> 180,091 XLM | <b>PNL:</b> $736 | <b>ROE:</b> 37.62%</p>
    <p><b>Status:</b> Jesse ON | When Ron Won | Ronism LIVE</p>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
