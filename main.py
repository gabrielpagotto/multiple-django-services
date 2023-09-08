import argparse, subprocess

# Lista de definição dos serviços
# Deve ser informado nome do serviço e porta onde será executado
services_def = [
    # (meu-servico-django, 3000),
]

parser = argparse.ArgumentParser(description="Usage: meu_script.py [options]")

def valid_ip(ip):
    octets = ip.split(".")
    if len(octets) != 4:
        return False
    for octet in octets:
        try:
            value = int(octet)
            if value < 0 or value > 255:
                return False
        except ValueError:
            return False
    return True

def exec_script_in_terminal(commands):
    commands_string = " && ".join(commands)
    print(commands_string)
    q_script = f"""
    tell application "Terminal"
        do script "{commands_string}"
    end tell
    """
    subprocess.run(["osascript", "-e", q_script], capture_output=True)

class Service():

    def __init__(self, name: str, port: int) -> None:
        self.name = name
        self.port = port
        self.dir_argument_name = f"--{name}-dir"
        self.parser_args_dest = f"{name}-dir".replace('-', '_')

    def add_arguments(self):
        parser.add_argument(
            self.dir_argument_name,
            help=f"Localização da pasta do serviço {self.name}",
            dest=self.parser_args_dest
        )

    def get_dir(self, parser_args):
        return parser_args.__getattribute__(self.parser_args_dest)

    def verify_dir(self, parser_args):
        if not self.get_dir(parser_args):
            print(f"Informe a localização do serviço '{self.name}' para continuar...\n")
            exit()

if __name__ == '__main__':
    parser.add_argument(
       "--ip",
        help="Endereço de IP onde os serviços serão inicializados",
        dest="ip_address",
    )

    services = []
    for service_def in services_def:
        service = Service(service_def[0], service_def[1])
        service.add_arguments()
        services.append(service)

    parser_args = parser.parse_args()
    ip_address = parser_args.ip_address

    if not ip_address:
        print("Informe um endereço de IP para continuar...\n")
        exit()

    if not valid_ip(ip_address):
        print(ip_address)
        print("Informe um endereço de IP válido...\n")
        exit()

    for service in services:
        service.verify_dir(parser_args)

    for service in services:
        exec_script_in_terminal(
            [
                f"cd {service.get_dir(parser_args)}",
                "git pull",
                "source venv/bin/activate",
                "pip install -r requirements.txt",
                f"python manage.py runserver {ip_address}:{service.port}",
            ]
        )
