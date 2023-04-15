from webui import initialize
import modules.interrogate

def initialize_auto_interrogator():
    initialize()
    interrogator = modules.interrogate.InterrogateModels("interrogate")
    interrogator.load()
    interrogator.categories()

if __name__ == "__main__":
    initialize_auto_interrogator()