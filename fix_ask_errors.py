from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
av = base / "apps/learning/ask_views.py"
avs = av.read_text(encoding="utf-8")
# Replace the provider call section with proper exception handling
old_section = '''    try:
        from apps.ai_gateway.services import AIGateway
        provider = AIGateway(institution=m.institution).provider
    except Exception:
        provider = None
    if provider is None:
        from apps.ai_gateway.providers.mock_provider import MockProvider
        provider = MockProvider()
    content = provider.generate(
        prompt,
        system_prompt="You are a school tutor. Cite the supplied context. If it is insufficient, say so.",
        mode="learner", curriculum=data.get("curriculum", ""), grade_level=data.get("grade", ""),
        language=data.get("language", "en"), subject=subject)'''
new_section = '''    provider = None
    try:
        from apps.ai_gateway.services import AIGateway
        provider = AIGateway(institution=m.institution).provider
    except Exception as e:
        pass
    if provider is None:
        from apps.ai_gateway.providers.mock_provider import MockProvider
        provider = MockProvider()
    try:
        content = provider.generate(
            prompt,
            system_prompt="You are a school tutor. Cite the supplied context. If it is insufficient, say so.",
            mode="learner", curriculum=data.get("curriculum", ""), grade_level=data.get("grade", ""),
            language=data.get("language", "en"), subject=subject)
    except Exception as e:
        content = "I apologize, but I encountered an error while generating your answer. Please try rephrasing your question or selecting a different subject."
        try:
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="LEARN_ASK_ERROR",
                                      resource_type="Conversation", resource_id=str(conv.id) if conv else "",
                                      metadata={"error": str(e), "question": q[:100]})
        except Exception:
            pass'''
if old_section in avs:
    avs = avs.replace(old_section, new_section, 1)
    av.write_text(avs, encoding="utf-8")
    print("ASK VIEW: EXCEPTION HANDLING ADDED")
else:
    print("WARNING: Could not find exact section to replace")
# Also add a fallback for Message creation
old_msg = '''    akwargs = {"conversation": conv, "content": content}
    if "role" in mf:
        akwargs["role"] = "assistant"
    amsg = Message.objects.create(**akwargs)'''
new_msg = '''    akwargs = {"conversation": conv, "content": content}
    if "role" in mf:
        akwargs["role"] = "assistant"
    try:
        amsg = Message.objects.create(**akwargs)
    except Exception as e:
        amsg = None'''
if old_msg in avs:
    avs = avs.replace(old_msg, new_msg, 1)
    av.write_text(avs, encoding="utf-8")
    print("ASK VIEW: MESSAGE CREATION PROTECTION ADDED")
# Wrap the entire response in a try/except
old_return = '''    return JsonResponse({"content": content, "sources": sources, "grounded": bool(chunks),
                         "web_source": web, "conversation_id": str(conv.id)})'''
new_return = '''    try:
        return JsonResponse({"content": content, "sources": sources, "grounded": bool(chunks),
                             "web_source": web, "conversation_id": str(conv.id)})
    except Exception as e:
        return JsonResponse({"content": "I encountered an error while preparing your response. Please try again.", 
                            "sources": [], "grounded": False, "web_source": None, 
                            "conversation_id": str(conv.id)}, status=200)'''
if old_return in avs:
    avs = avs.replace(old_return, new_return, 1)
    av.write_text(avs, encoding="utf-8")
    print("ASK VIEW: RESPONSE ERROR HANDLING ADDED")
