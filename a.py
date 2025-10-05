import base64

with open("yourfile.pdf", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()
    print(f"data:application/pdf;base64,{encoded}")
