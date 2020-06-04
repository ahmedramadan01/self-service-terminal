from subprocess import run

def get_cups_status():
    args = ['lpstat', '-t']
    out = run(args, capture_output=True)
    return out.stdout.decode()