from potassium import Potassium, Request, Response

import torch
import webui
import shared
import modules.safe as safe

app = Potassium("my_app")

shared.init()

torch.load = safe.unsafe_torch_load
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

list_models = None
load_model = None

def noop(*args, **kwargs):
    pass

def unload_model():
    from modules import shared as auto_shared, sd_hijack, devices
    import gc
    if auto_shared.sd_model:
         sd_hijack.model_hijack.undo_hijack(auto_shared.sd_model)
         auto_shared.sd_model = None
         gc.collect()
         devices.torch_gc()

def register_model():
    global model
    try:
        from modules import shared as auto_shared, sd_hijack
        if auto_shared.sd_model is not model:
            unload_model()
            auto_shared.sd_model = model
            sd_hijack.model_hijack.hijack(model)
            print("Loaded default model.")
    except:
        print("Failed to hijack model.")


def load_model_by_url(url):
    global list_models, load_model
    import modules.sd_models
    import hashlib
    hash_object = hashlib.md5(url.encode())
    md5_hash = hash_object.hexdigest()

    from download_checkpoint import download
    download(url, md5_hash)

    modules.sd_models.list_models = list_models
    modules.sd_models.load_model = load_model

    modules.sd_models.list_models()

    for m in modules.sd_models.checkpoints_list.values():
        if md5_hash in m.name:
            load_model(m)
            break

    modules.sd_models.list_models = noop
    modules.sd_models.load_model = noop

# @app.init runs at startup, and loads models into the app's context
@app.init
def init():
    global model, list_models, load_model
    import modules.sd_models

    modules.sd_models.list_models()

    list_models = modules.sd_models.list_models
    modules.sd_models.list_models = noop

    model = modules.sd_models.load_model()

    load_model = modules.sd_models.load_model
    modules.sd_models.load_model = noop

    register_model()
   
    context = {
        "model": model
    }

    return context

# @app.handler runs for every call
@app.handler()
def handler(context: dict, request: Request) -> Response:
    if shared.client is None:
        return Response(
            json={"success": False, "error": "Automatic1111's webui api not initialized."},
            status=500
        )
    model_input = request.json
    
    params = None

    if 'endpoint' in model_input:
        endpoint = model_input['endpoint']
        if 'params' in model_input:
            params = model_input['params']
    else:
        endpoint = 'txt2img'
        params = model_input

    if endpoint == 'txt2img' or endpoint == 'img2img':
        if 'width' not in params:
            params['width'] = 768
        if 'height' not in params:
            params['height'] = 768

    if endpoint == 'txt2img':
        if 'num_inference_steps' in params:
            params['steps'] = params['num_inference_steps']
            del params['num_inference_steps']
        if 'guidance_scale' in params:
            params['cfg_scale'] = params['guidance_scale']
            del params['guidance_scale']

    if params is not None:
        response = shared.client.post('/sdapi/v1/' + endpoint, json = params)
    else:
        response = shared.client.get('/sdapi/v1/' + endpoint)

    output = response.json()

    if 'images' in output:
        output = {
            "images": output["images"]
        }

    output["callParams"] = params

    return Response(
        json = output, 
        status=200
    )

if __name__ == "__main__":
    app.serve()
    webui.api_only()