import json
from datetime import datetime
from app.prompts import Verifier, Refiner
from app.services.llm_service import run_model
from app.utils.parsers import extract_json_from_response


class AuditService:
    @staticmethod
    def needs_refinement(audit_response: str) -> tuple[bool, dict]:
        """
        Check if the audit response indicates refinement is needed.
        Returns (needs_refinement, parsed_audit_dict)

        """
        try:
            cleaned_response = extract_json_from_response(audit_response)

            audit_data = json.loads(cleaned_response)
            
            findings = audit_data.get('findings', [])

            if len(findings) > 0:
                return True, audit_data
            else:
                return False, audit_data
            
        except Exception as e:
            print(f"Error parsing audit response as json: {e}")
            return True, {}
    
    @staticmethod
    async def orchestrate_agents(code_input: dict, user_request: str, max_iterations: int = 3) -> dict: 
        """
        Orchestrates the verifier and refiner agents.

        Args:
            code_input: Dictionary containing 'html', 'ts', 'css' keys
            user_request: The original user request for functional validation
            max_iterations: Maximum number of refinement iterations (default: 3)

        Returns:
            Final refined code or original code if no refinement needed
        """
        current_code = code_input.copy()
        iteration = 0
        previous_health_score = None
        previous_audit_data = None
        best_code = code_input.copy()
        best_health_score = 0
        best_audit_data = {}
        best_iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"ITERATION {iteration}/{max_iterations}")
            #Prepare prompt
            user_prompt_verifier = Verifier.format_verifier_user_prompt(
                                            current_code,
                                            user_request,
                                            iteration,
                                            previous_audit_data
                                        )
            #call verifier agent                    
            try:
                audit_response = await run_model(
                    Verifier.system_prompt,
                    user_prompt_verifier
                )
            except Exception as e:
                print(f"Error calling verifier agent: {e}")
                break

            needs_refine, audit_data = AuditService.needs_refinement(audit_response) 

            #trackscores
            current_health_score = audit_data.get('audit_summary', {}).get('health_score', 0) or 0

            if current_health_score > best_health_score:
                best_code = current_code.copy()
                best_health_score = current_health_score
                best_audit_data = audit_data
                best_iteration = iteration
            if not needs_refine:
                return current_code
            
            #refinement step
            if iteration < max_iterations:
                user_prompt_refiner = Refiner.format_refiner_user_prompt(
                    current_code,
                    audit_data,
                    user_request
                )
                try:
                    refined_response = await run_model(
                        Refiner.system_prompt,
                        user_prompt_refiner
                    )
                    cleaned_refined = extract_json_from_response(refined_response)
                    current_code = json.loads(cleaned_refined)
                
                    previous_audit_data = audit_data
                    previous_health_score = current_health_score

                except Exception as e:
                    print(f"Error calling refiner agent: {e}")
                    return current_code
                    
        return best_code