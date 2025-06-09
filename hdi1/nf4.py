import torch
from transformers import LlamaForCausalLM, PreTrainedTokenizerFast
import sys
import os

# Add parent directory to path for direct execution
if __name__ == "__main__":
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

# Check if bitsandbytes is available
try:
    import bitsandbytes as bnb
    print("✅ bitsandbytes available")
except ImportError:
    print("⚠️ bitsandbytes not available - 4-bit quantization will be disabled")

# Handle imports for both direct execution and module import
try:
    from . import HiDreamImagePipeline
    from . import HiDreamImageTransformer2DModel
    from .schedulers.fm_solvers_unipc import FlowUniPCMultistepScheduler
    from .schedulers.flash_flow_match import FlashFlowMatchEulerDiscreteScheduler
except ImportError:
    # Fallback for direct execution
    from hdi1 import HiDreamImagePipeline
    from hdi1 import HiDreamImageTransformer2DModel
    from hdi1.schedulers.fm_solvers_unipc import FlowUniPCMultistepScheduler
    from hdi1.schedulers.flash_flow_match import FlashFlowMatchEulerDiscreteScheduler


MODEL_PREFIX = "azaneko"
LLAMA_MODEL_NAME = "unsloth/Meta-Llama-3.1-8B-Instruct"


# Model configurations
MODEL_CONFIGS = {
    "dev": {
        "path": f"{MODEL_PREFIX}/HiDream-I1-Dev-nf4",
        "guidance_scale": 0.0,
        "num_inference_steps": 28,
        "shift": 6.0,
        "scheduler": FlashFlowMatchEulerDiscreteScheduler
    },
    "full": {
        "path": f"{MODEL_PREFIX}/HiDream-I1-Full-nf4",
        "guidance_scale": 5.0,
        "num_inference_steps": 50,
        "shift": 3.0,
        "scheduler": FlowUniPCMultistepScheduler
    },
    "fast": {
        "path": f"{MODEL_PREFIX}/HiDream-I1-Fast-nf4",
        "guidance_scale": 0.0,
        "num_inference_steps": 16,
        "shift": 3.0,
        "scheduler": FlashFlowMatchEulerDiscreteScheduler
    }
}


def log_vram(msg: str):
    print(f"{msg} (used {torch.cuda.memory_allocated() / 1024**2:.2f} MB VRAM)\n")


def load_models(model_type: str):
    config = MODEL_CONFIGS[model_type]
    
    tokenizer_4 = PreTrainedTokenizerFast.from_pretrained(LLAMA_MODEL_NAME)
    log_vram("✅ Tokenizer loaded!")
    
    # Load text encoder without quantization
    text_encoder_4 = LlamaForCausalLM.from_pretrained(
        LLAMA_MODEL_NAME,
        output_hidden_states=True,
        output_attentions=True,
        return_dict_in_generate=True,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    log_vram("✅ Text encoder loaded!")

    try:
        transformer = HiDreamImageTransformer2DModel.from_pretrained(
            config["path"],
            subfolder="transformer",
            torch_dtype=torch.bfloat16
        )
        log_vram("✅ Transformer loaded!")
    except Exception as e:
        print(f"❌ Failed to load transformer: {e}")
        # Try loading without torch_dtype specification
        transformer = HiDreamImageTransformer2DModel.from_pretrained(
            config["path"],
            subfolder="transformer"
        )
        log_vram("✅ Transformer loaded (fallback)!")
    
    try:
        pipe = HiDreamImagePipeline.from_pretrained(
            config["path"],
            scheduler=config["scheduler"](num_train_timesteps=1000, shift=config["shift"], use_dynamic_shifting=False),
            tokenizer_4=tokenizer_4,
            text_encoder_4=text_encoder_4,
            torch_dtype=torch.bfloat16,
        )
        pipe.transformer = transformer
        log_vram("✅ Pipeline loaded!")
        pipe.enable_sequential_cpu_offload()
    except Exception as e:
        print(f"❌ Failed to load pipeline: {e}")
        # Try without torch_dtype
        pipe = HiDreamImagePipeline.from_pretrained(
            config["path"],
            scheduler=config["scheduler"](num_train_timesteps=1000, shift=config["shift"], use_dynamic_shifting=False),
            tokenizer_4=tokenizer_4,
            text_encoder_4=text_encoder_4,
        )
        pipe.transformer = transformer
        log_vram("✅ Pipeline loaded (fallback)!")
        pipe.enable_sequential_cpu_offload()
    
    return pipe, config


@torch.inference_mode()
def generate_image(pipe: HiDreamImagePipeline, model_type: str, prompt: str, resolution: tuple[int, int], seed: int):
    # Get configuration for current model
    config = MODEL_CONFIGS[model_type]
    guidance_scale = config["guidance_scale"]
    num_inference_steps = config["num_inference_steps"]
    
    # Parse resolution
    width, height = resolution
 
    # Handle seed
    if seed == -1:
        seed = torch.randint(0, 1000000, (1,)).item()
    
    # Check if CUDA is available, fallback to CPU if needed
    device = "cuda" if torch.cuda.is_available() else "cpu"
    generator = torch.Generator(device).manual_seed(seed)
    
    try:
        images = pipe(
            prompt,
            height=height,
            width=width,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            num_images_per_prompt=1,
            generator=generator
        ).images
        
        return images[0], seed
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        print("🔄 Retrying with reduced precision...")
        
        # Try with different settings
        try:
            images = pipe(
                prompt,
                height=height,
                width=width,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=1,
                generator=generator
            ).images
            
            return images[0], seed
        except Exception as e2:
            raise RuntimeError(f"Image generation failed even with fallback: {e2}") from e2

