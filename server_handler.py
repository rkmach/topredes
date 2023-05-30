from functools import partial
import json
import io
import os

def get_current_db():
    path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(path, 'data.json')

    f = open(json_path, 'r+')
    
    # `db` eh um dicionário
    try:
        db = json.load(f)
        return json.dumps(db)
    except Exception:
        print("Erro ao acessar o banco de dados")
        return None

def handle_delete(f: io.TextIOWrapper, db: dict, key: str, *args):
    if not key:
        return 404
    
    # Entra aqui caso queria remover um valor específico de uma chave
    if len(args) == 1:
        values_to_remove = args[0].split(',')
        try:
            values: list = db[key]
            for value in values_to_remove:
                values.remove(value)
            f.seek(0)
            json.dump(db, f)
            f.truncate()
            return '201 - [green]Valor(es) removido(s) com sucesso[/green]'
        except Exception:
            return '404 - [red]Não foi possível realizar a remoção, confira os dados fornecidos e tente novamente[/red]'
    
    if key in db.keys():
        # Remover a entrada
        del db[key]
        
        f.seek(0)
        json.dump(db, f)
        f.truncate()
        return '201 - [green]Entrada removida com sucesso[/green]'
    else:
        return '404 - [red]Não foi possível remover a entrada, porque ela não existe no banco de dados[/red]'

def handle_edit(f: io.TextIOWrapper, db: dict, key: str, value: str, *args):
    if not key:
        return '404 - [red]Não foi possível alterar a entrada, porque ela não existe no banco de dados[/red]'
    
    if not value:
        return '404 - [red]Não foi possível alterar a entrada, porque o valor não foi especificado[/red]'
    
    # Entra aqui caso queria alterar um valor específico de uma chave
    if len(args) == 1:
        value_to_change = args[0]
        
        try:
            values: list = db[key]
            for i, old_value in enumerate(values):
                if old_value == value:
                    values[i] = value_to_change
                    break
            f.seek(0)
            json.dump(db, f)
            f.truncate()
            return '201 - [green]Valor(es) alterado(s) com sucesso[/green]'
        except Exception:
            return '404 - [red]Não foi possível realizar a alteração, confira os dados fornecidos e tente novamente[/red]'
    
    if key in db.keys():
        # atualizar o valor referente a chave
        db[key] = value.split(',')
        
        f.seek(0)
        json.dump(db, f)
        f.truncate()
        return "201 - [green]Entrada atualizada com sucesso![/green]"
    else:
        return '404 - [red]Não foi possível alterar a entrada, porque ela não existe no banco de dados[/red]'

def handle_add(f: io.TextIOWrapper, db: dict, key: str, value: str):
    if not key:
        return '404 - [red]Não foi possível adicionar a entrada, porque a chave não foi especificada[/red]'
    
    if not value:
        return '404 - [red]Não foi possível adicionar a entrada, porque o valor não foi especificado[/red]'
    
    if key in db.keys():
        return '404 - [red]Não foi possível alterar a entrada, porque ela não existe no banco de dados[/red]'
    
    new_entry = {key: value.split(',')}
    merged = dict(**db, **new_entry)
    f.seek(0)
    json.dump(merged, f)
    f.truncate()
    return "201 - [green]Entrada adicionada com sucesso![/green]"

def handle(received_data: bytes, f:io.TextIOWrapper, db:dict):
     
    # Rodar a função que trata cada um dos verbos
    # Cada uma das funções retorna um código de sucesso, caso tudo tenha corrido bem
    # Ou um código de erro, caso algum tenha ocorrido
    try:
        data = received_data.decode().split()
        print(data)
        verb = data[0]
        
        if verb == "remover":
            func = partial(handle_delete, f, db, data[1])
            # remover chave valores
            if len(data) == 3:
                func = partial(func, data[2])
                return func()
            # remover chave
            return func()
        
        if verb == "adicionar":
            return handle_add(f, db, data[1], data[2])
        
        if verb == "alterar":
            func = partial(handle_edit, f, db, data[1], data[2])
            # alterar chave valor valor
            if len(data) == 4:
                func = partial(func, data[3])
                return func()
            # alterar chave valores
            return func()
        if verb == 'consultar':
            return '200 - [green]Banco de dados recuperado com sucesso[/]'
        return '404 - [red]Os comandos disponíveis são: adicionar, alterar, remover ou consultar[/]'
        
    except Exception:
        return '404 - [red]Os comandos disponíveis são: adicionar, alterar, remover ou consultar[/]'
