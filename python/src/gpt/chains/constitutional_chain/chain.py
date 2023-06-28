from typing import Union

from gpt.chains.constitutional_chain.principle_chain import create_generate_principle_chain
from gpt.chains.constitutional_chain.prompt import CRITIQUE_PROMPT, REVISION_PROMPT

from typing import Any, Dict, List, Optional

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chains.constitutional_ai.models import ConstitutionalPrinciple
from langchain.chains.constitutional_ai.principles import PRINCIPLES
from langchain.chains.llm import LLMChain


class ConstitutionalChain(Chain):
    """Chain for applying constitutional principles to another chain."""

    chain: LLMChain
    constitutional_principles: List[ConstitutionalPrinciple]
    critique_chain: LLMChain
    revision_chain: LLMChain

    return_intermediate_steps: bool = False
    return_initial_output: bool = True

    @classmethod
    def get_principles(
        cls, names: Optional[List[str]] = None
    ) -> List[ConstitutionalPrinciple]:
        if names is None:
            return list(PRINCIPLES.values())
        else:
            return [PRINCIPLES[name] for name in names]

    @classmethod
    def get_principle(cls, llm: BaseLanguageModel, principle: Union[ConstitutionalPrinciple, str]) -> ConstitutionalPrinciple:
        if isinstance(principle, str):
            if principle in PRINCIPLES.keys():
                principle = PRINCIPLES[principle]
            else:
                # generate a full ConstitutionalPrinciple from a user description
                principle = create_generate_principle_chain(llm).run(principle)
                print("Generated ConstitutionalPrinciple from user description:")
                print(str(principle))
        return principle

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        chain: LLMChain,
        principle: Union[ConstitutionalPrinciple, str],
        **kwargs: Any,
    ) -> "ConstitutionalChain":
        """Create a chain from an LLM."""
        critique_chain = LLMChain(llm=llm, prompt=CRITIQUE_PROMPT)
        revision_chain = LLMChain(llm=llm, prompt=REVISION_PROMPT)
        return cls(
            chain=chain,
            critique_chain=critique_chain,
            revision_chain=revision_chain,
            constitutional_principles=[
                cls.get_principle(llm, principle)
            ],
            **kwargs,
        )

    @property
    def input_keys(self) -> List[str]:
        """Defines the input keys."""
        return self.chain.input_keys

    @property
    def output_keys(self) -> List[str]:
        """Defines the output keys."""
        k = ["output"]
        if self.return_intermediate_steps:
            k += ["critiques_and_revisions"]
        if self.return_initial_output:
            k += ["initial_text"]
        return k

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()

        response = self.chain.run(
            **inputs,
            callbacks=_run_manager.get_child("original"),
        )
        initial_response = response
        #input_prompt = self.chain.prompt.format(**inputs)

        _run_manager.on_text(
            text="Initial response: " + response + "\n\n",
            verbose=self.verbose,
            color="yellow",
        )

        critiques_and_revisions = []
        for constitutional_principle in self.constitutional_principles:
            # Do critique
            raw_critique = self.critique_chain.run(
                #input_prompt=input_prompt,
                output_from_model=response,
                critique_request=constitutional_principle.critique_request,
                callbacks=_run_manager.get_child("critique"),
            )
            critique = self._parse_critique(
                output_string=raw_critique,
            ).strip()

            # if the critique contains "No critique needed", then we're done
            # in this case, initial_output is the same as output,
            # but we'll keep it for consistency
            if "no critique needed" in critique.lower():
                critiques_and_revisions.append((critique, ""))
                continue

            # Do revision
            revision = self.revision_chain.run(
                #input_prompt=input_prompt,
                output_from_model=response,
                critique_request=constitutional_principle.critique_request,
                critique=critique,
                revision_request=constitutional_principle.revision_request,
                callbacks=_run_manager.get_child("revision"),
            ).strip()
            response = revision
            critiques_and_revisions.append((critique, revision))

            _run_manager.on_text(
                text=f"Applying {constitutional_principle.name}..." + "\n\n",
                verbose=self.verbose,
                color="green",
            )

            _run_manager.on_text(
                text="Critique: " + critique + "\n\n",
                verbose=self.verbose,
                color="blue",
            )

            _run_manager.on_text(
                text="Updated response: " + revision + "\n\n",
                verbose=self.verbose,
                color="yellow",
            )

        final_output: Dict[str, Any] = {"output": response}
        if self.return_initial_output:
            final_output["initial_text"] = initial_response
        if self.return_intermediate_steps:
            final_output["critiques_and_revisions"] = critiques_and_revisions
        return final_output

    @staticmethod
    def _parse_critique(output_string: str) -> str:
        if "Revision request:" not in output_string:
            return output_string
        output_string = output_string.split("Revision request:")[0]
        if "\n\n" in output_string:
            output_string = output_string.split("\n\n")[0]
        return output_string
