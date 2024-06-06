from utils.digital_human.realtime_inference import digital_human_preprocess
from utils.infer.load_infer_model import load_hf_model, load_turbomind_model
from utils.tts.gpt_sovits.inference_gpt_sovits import get_tts_model
from utils.web_configs import WEB_CONFIGS

# ==================================================================
#                               TTS 模型
# ==================================================================

if WEB_CONFIGS.ENABLE_TTS:
    # samber
    # from utils.tts.sambert_hifigan.tts_sambert_hifigan import get_tts_model
    # TTS_HANDLER = get_tts_model()

    # gpt_sovits
    TTS_HANDLER = get_tts_model()
else:
    TTS_HANDLER = None

# ==================================================================
#                             数字人 模型
# ==================================================================

if WEB_CONFIGS.ENABLE_DIGITAL_HUMAN:
    DIGITAL_HUMAN_HANDLER = digital_human_preprocess(
        model_dir=WEB_CONFIGS.DIGITAL_HUMAN_MODEL_DIR,
        use_float16=False,
        video_path=WEB_CONFIGS.DIGITAL_HUMAN_VIDEO_PATH,
        work_dir=WEB_CONFIGS.DIGITAL_HUMAN_GEN_PATH,
        fps=WEB_CONFIGS.DIGITAL_HUMAN_FPS,
        bbox_shift=WEB_CONFIGS.DIGITAL_HUMAN_BBOX_SHIFT,
    )
else:
    DIGITAL_HUMAN_HANDLER = None


# ==================================================================
#                               LLM 模型
# ==================================================================

# 加载 LLM 模型
if WEB_CONFIGS.USING_LMDEPLOY:
    load_model_func = load_turbomind_model
else:
    load_model_func = load_hf_model

LLM_MODEL, LLM_TOKENIZER, RAG_RETRIEVER = load_model_func(
    WEB_CONFIGS.LLM_MODEL_DIR,
    enable_rag=WEB_CONFIGS.ENABLE_RAG,
    rag_config=WEB_CONFIGS.RAG_CONFIG_PATH,
    db_path=WEB_CONFIGS.RAG_VECTOR_DB_DIR,
)
