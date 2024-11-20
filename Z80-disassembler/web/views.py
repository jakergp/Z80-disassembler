from django.shortcuts import render, HttpResponse
from core.hex_reader import hex_reader
from core.disassembler import Dissasembler

# Create your views here.
def disassemble(request):
    if request.method == "GET":
        hex_code = request.GET.get('original')
        if hex_code is None:
            hex_code=""

        code = hex_reader(hex_code)

        if code is None:
            return render(request, "index.html", {"original_code": hex_code, "disassembled_code": "El código proporcionado es inválido"})

        disassembler = Dissasembler()

        code_list = disassembler.disassemble(code)

        disassembled_code = ""
        for line in code_list:
           disassembled_code += line + '\n'

        return render(request, "index.html", {"original_code": hex_code, "disassembled_code": disassembled_code})
