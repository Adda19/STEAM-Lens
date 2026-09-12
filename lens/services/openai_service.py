import base64
import json
import logging
from django.conf import settings
from openai import OpenAI, OpenAIError
from pydantic import ValidationError
from lens.prompts.analyze import INSTRUCTIONS as ANALYZE
from lens.prompts.coach import INSTRUCTIONS as COACH
from lens.schemas.analysis import Analysis
from lens.schemas.coach import CoachReply

logger = logging.getLogger(__name__)

class ProviderUnavailable(Exception):
    pass

def _request(schema, **kwargs):
    if not settings.OPENAI_API_KEY:
        raise ProviderUnavailable("missing_configuration")
    try:
        with OpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT, max_retries=0) as client:
            response = client.responses.parse(model=settings.OPENAI_MODEL, text_format=schema,
                                              max_output_tokens=3500, store=True, **kwargs)
        if response.status != "completed" or response.output_parsed is None:
            raise ProviderUnavailable("incomplete_response")
        return response.output_parsed, response.id
    except (OpenAIError, ValidationError, ValueError) as exc:
        # Never log request bodies, images, student replies or provider error text.
        logger.warning("Provider request failed (%s)", type(exc).__name__)
        raise ProviderUnavailable("provider_error") from None

def analyze(image_bytes, context):
    uri = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("ascii")
    result, response_id = _request(Analysis, instructions=ANALYZE, input=[{"role": "user", "content": [
        {"type": "input_text", "text": json.dumps(context, ensure_ascii=False)},
        {"type": "input_image", "image_url": uri, "detail": "auto"}]}])
    if result.valid_capture and result.mission.estimated_minutes > context["available_time"]:
        raise ProviderUnavailable("invalid_duration")
    return result, response_id

def coach(answer, context, mission, previous_response_id):
    return _request(CoachReply, instructions=COACH, previous_response_id=previous_response_id,
                    input=[{"role": "user", "content": json.dumps({"context": context, "mission": mission,
                            "student_answer": answer}, ensure_ascii=False)}])
