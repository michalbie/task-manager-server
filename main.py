import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import ast

class MyServer(BaseHTTPRequestHandler):

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        BaseHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        if(self.path == "/getTasks"):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            f = open("tasks.json", "r")
            text = f.read()
            self.wfile.write(str.encode(text))


    def do_POST(self):
        if (self.path == "/generateTask"):
            self.send_response(200)
            self.end_headers()
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            sequence = body.decode("utf-8")[1:-1]
            inputs = tokenizer.encode(sequence, return_tensors='pt')
            outputs = model.generate(inputs, max_length=50, do_sample=True, temperature=1)
            text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            with open('tasks.json', 'r') as f:
                data = json.load(f)
                if len(data['tasks']) > 0:
                    lastIndex = data['tasks'][len(data['tasks'])-1]['id']
                else:
                    lastIndex = -1
                data['tasks'].append({'id': lastIndex+1, 'text': text, 'status': 'Generated'})

            with open('tasks.json', 'w') as f:
                f.write(json.dumps(data))

            self.wfile.write(str.encode(json.dumps(data)))

        elif (self.path == "/updateTask"):
            self.send_response(200)
            self.end_headers()
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            stringifiedBody = body.decode("utf-8")
            body = ast.literal_eval(stringifiedBody)
            result = []

            if(body["action"] == "CONFIRM"):
                with open('tasks.json', 'r') as f:
                    data = json.load(f)

                    #update task's status of the given id
                    for task in data['tasks']:
                        if task['id'] == body['id']:
                            task['status'] = "Confirmed"
                        result.append(task)

                with open('tasks.json', 'w') as f:
                    f.write(json.dumps({'tasks': result}))

            elif (body["action"] == "REMOVE"):
                with open('tasks.json', 'r') as f:
                    data = json.load(f)

                    # remove task of the given id
                    for task in data['tasks']:
                        if task['id'] != body['id']:
                            result.append(task)

                with open('tasks.json', 'w') as f:
                    f.write(json.dumps({'tasks': result}))

            self.wfile.write(str.encode(json.dumps({'tasks': result})))

if __name__ == "__main__":
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2", pad_token_id=tokenizer.eos_token_id)

    httpd = HTTPServer(('localhost', 8000), MyServer)
    httpd.serve_forever()

