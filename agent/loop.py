from agent.tools import SYSTEM_ROLE, AgentResponse, AgentAction
from config import CLIENT, GEMINI_MODEL
from agent.browser import Browser
import asyncio
from google.genai import types
from termcolor import colored


def colored_print(text: str, color: str, **kwargs):
    print(colored(text, color), **kwargs)


async def generate_response(history, retry_count=3):
    if retry_count == 0:
        return "STOP"
    try:
        result = CLIENT.models.generate_content(
            model=GEMINI_MODEL,
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=types.Part.from_text(text=SYSTEM_ROLE),
                response_mime_type="application/json",
                response_schema=AgentResponse,
            ),
        )
    except Exception as e:
        colored_print(f"An error occurred: {e}. Retrying...", "red")
        await asyncio.sleep(2)
        return await generate_response(history, retry_count - 1)

    return result.text


async def build_user_prompt(user_input: str, current_ui: str, is_stuck=False):
    stuck_msg = (
        "\n\nWARNING: The UI state has not changed since the last turn. Your previous actions may have had no effect. Consider using 'wait_user' or a different strategy."
        if is_stuck
        else ""
    )
    prompt = f"""
Current UI:
{current_ui}
{stuck_msg}

User Request: {user_input}
"""
    return types.Content(role="user", parts=[types.Part.from_text(text=prompt)])


async def execute_action(action: AgentAction, browser: Browser):
    tool_name = action.title
    try:
        colored_print(f"Executing: {tool_name} - {action}", "cyan")

        if tool_name == "click":
            return await browser.click(action.target)
        elif tool_name == "type":
            return await browser.type(action.target, action.value)
        elif tool_name == "go_to":
            await browser.goto(action.url)
            return f"Navigated to {action.url}"
        elif tool_name == "wait_user":
            reason = action.reason or "manual action"
            colored_print(f"\n[PAUSED] {reason}", "magenta")
            input("Press Enter once you have finished...")
            return "User finished manual action"
        elif tool_name == "ask_user":
            question = action.question or "Please provide the missing information."
            colored_print(f"\n[QUESTION] {question}", "blue")
            user_response = input("Your answer: ")
            return f"User answered: {user_response}"
        elif tool_name == "stop":
            return "STOP"
        else:
            return f"Unknown action: {tool_name}"
    except Exception as e:
        return f"ERROR: {str(e)}"


async def agent_loop(user_request: str):
    browser = Browser()
    await browser.start()
    history = []
    last_ui_state = None

    try:
        current_request = user_request
        while True:
            ui_state = await browser.get_ui_state()

            # Detect stuck state
            is_stuck = ui_state == last_ui_state
            last_ui_state = ui_state

            user_prompt = await build_user_prompt(
                current_request, ui_state, is_stuck=is_stuck
            )
            history.append(user_prompt)

            response_text = await generate_response(history)
            if response_text == "STOP":
                break

            history.append(
                types.Content(
                    role="model", parts=[types.Part.from_text(text=response_text)]
                )
            )

            try:
                response_data = AgentResponse.model_validate_json(response_text)
                actions = response_data.actions
            except Exception as e:
                history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=f"Error parsing JSON: {e}")],
                    )
                )
                continue

            results = []
            turn_user_response = None
            for action in actions:
                result = await execute_action(action, browser)
                results.append(result)

                if action.title == "ask_user":
                    turn_user_response = result  # This contains "User answered: ..."

                if result.startswith("ERROR") or action.title in [
                    "go_to",
                    "wait_user",
                    "ask_user",
                    "stop",
                ]:
                    break
                # Smaller sleep between actions, trust get_ui_state's wait_for_load_state
                await asyncio.sleep(0.2)

            if "STOP" in results:
                break

            history.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text="Turn Results:\n" + "\n".join(results)
                        )
                    ],
                )
            )
            if turn_user_response:
                current_request = f"User provided context: '{turn_user_response}'. Use this to continue the task."
            else:
                current_request = "Continue with the task."

    except KeyboardInterrupt:
        colored_print("\nInterrupted.", "red")
    except Exception as e:
        colored_print(f"Critical Error: {e}", "red")
    finally:
        await browser.stop()


