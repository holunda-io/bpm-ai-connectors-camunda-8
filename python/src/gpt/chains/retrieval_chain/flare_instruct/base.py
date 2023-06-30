from typing import Optional, List, Any, Dict

from langchain import LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import CallbackManagerForChainRun
from langchain.chains.base import Chain
from langchain.chains.retrieval_qa.base import BaseRetrievalQA
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseRetriever

from gpt.chains.retrieval_chain.flare_instruct.answer_inserter.answer_inserter import LLMLookaheadAnswerInserter, BaseLookaheadAnswerInserter
from gpt.chains.retrieval_chain.flare_instruct.output_parser import IsDoneOutputParser, QueryTaskOutputParser
from gpt.chains.retrieval_chain.flare_instruct.prompt import DEFAULT_INSTRUCT_PROMPT, HUMAN_MESSAGE_TEMPLATE


class FLAREInstructChain(Chain):

    input_key: str = "query"  #: :meta private:
    output_key: str = "result"  #: :meta private:

    instruct_chain: LLMChain
    retrieval_qa: BaseRetrievalQA
    retriever: BaseRetriever

    lookahead_answer_inserter: BaseLookaheadAnswerInserter
    done_output_parser: IsDoneOutputParser
    query_task_output_parser: QueryTaskOutputParser
    max_iterations: int = 10
    max_lookahead_query_tasks: int = 1

    verbose = True

    @property
    def input_keys(self) -> List[str]:
        """Return the input keys.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Return the output keys.

        :meta private:
        """
        return [self.output_key]

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        retrieval_qa: BaseRetrievalQA,
        retriever: BaseRetriever,
        **kwargs: Any,
    ) -> "FLAREInstructChain":
        """Initialize from LLM."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                DEFAULT_INSTRUCT_PROMPT
            ),
            HumanMessagePromptTemplate.from_template(
                HUMAN_MESSAGE_TEMPLATE
            )
        ])
        instruct_chain = LLMChain(
            llm=llm,
            prompt=prompt
        )
        return cls(
            llm=llm,
            instruct_chain=instruct_chain,
            retriever=retriever,
            retrieval_qa=retrieval_qa,
            lookahead_answer_inserter=LLMLookaheadAnswerInserter.from_llm(llm=llm),
            done_output_parser=IsDoneOutputParser(),
            query_task_output_parser=QueryTaskOutputParser(),
            **kwargs
        )

    def _get_relevant_lookahead_response(self, updated_lookahead_resp: str) -> str:
        """Get relevant lookahead response."""
        # if there's remaining query tasks, then truncate the response
        # until the start position of the first tag
        # there may be remaining query tasks because the _max_lookahead_query_tasks
        # is less than the total number of generated [Search(query)] tags
        remaining_query_tasks = self.query_task_output_parser.parse(
            updated_lookahead_resp
        )
        if len(remaining_query_tasks) == 0:
            relevant_lookahead_resp = updated_lookahead_resp
        else:
            first_task = remaining_query_tasks[0]
            relevant_lookahead_resp = updated_lookahead_resp[: first_task.start_idx]
        return relevant_lookahead_resp

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """Query and get response."""
        query = inputs[self.input_key]
        print(f"Query: {query}\n")

        init_docs = self.retriever.get_relevant_documents(query)
        init_doc_str = "\n\n".join([d.page_content for d in init_docs])

        cur_response = ""
        for iter in range(self.max_iterations):
            if self.verbose:
                print(f"Current response: {cur_response}\n")
            # generate "lookahead response" that contains "[Search(query)]" tags
            # e.g.
            # The colors on the flag of Ghana have the following meanings. Red is
            # for [Search(Ghana flag meaning)],...
            lookahead_resp = self.instruct_chain.run(
                context=init_doc_str,
                query_str=query,
                existing_answer=cur_response,
            )

            lookahead_resp = lookahead_resp.strip()
            if self.verbose:
                print(f"Lookahead response: {lookahead_resp}\n")

            is_done, fmt_lookahead = self.done_output_parser.parse(lookahead_resp)
            if is_done:
                cur_response = cur_response.strip() + " " + fmt_lookahead.strip()
                break

            # parse lookahead response into query tasks
            query_tasks = self.query_task_output_parser.parse(lookahead_resp)

            # get answers for each query task
            query_tasks = query_tasks[: self.max_lookahead_query_tasks]
            query_answers = []
            for _, query_task in enumerate(query_tasks):
                query_answer = self.retrieval_qa.run(query_task.query_str)
                query_answers.append(query_answer)

            # fill in the lookahead response template with the query answers
            # from the query engine
            updated_lookahead_resp = self.lookahead_answer_inserter.insert(
                lookahead_resp, query_tasks, query_answers, prev_response=cur_response
            )

            # get "relevant" lookahead response by truncating the updated
            # lookahead response until the start position of the first tag
            # also remove the prefix from the lookahead response, so that
            # we can concatenate it with the existing response
            relevant_lookahead_resp_wo_prefix = self._get_relevant_lookahead_response(
                updated_lookahead_resp
            )

            if self.verbose:
                print(
                    "Updated lookahead response: "
                    + f"{relevant_lookahead_resp_wo_prefix}\n",
                )

            # append the relevant lookahead response to the final response
            cur_response = (
                cur_response.strip() + " " + relevant_lookahead_resp_wo_prefix.strip()
            )

        return {self.output_key: cur_response}
