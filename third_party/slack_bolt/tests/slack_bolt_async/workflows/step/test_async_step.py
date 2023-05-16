import pytest

from slack_bolt import Ack
from slack_bolt.error import BoltError
from slack_bolt.workflows.step.async_step import AsyncWorkflowStep


class TestStep:
    def test_build(self):
        step = AsyncWorkflowStep.builder("foo")
        step.edit(just_ack)
        step.save(just_ack)
        step.execute(just_ack)
        assert step.build() is not None

    def test_build_errors(self):
        with pytest.raises(BoltError):
            step = AsyncWorkflowStep.builder("foo")
            step.save(just_ack)
            step.execute(just_ack)
            step.build()
        with pytest.raises(BoltError):
            step = AsyncWorkflowStep.builder("foo")
            step.edit(just_ack)
            step.execute(just_ack)
            step.build()
        with pytest.raises(BoltError):
            step = AsyncWorkflowStep.builder("foo")
            step.edit(just_ack)
            step.save(just_ack)
            step.build()


def just_ack(ack: Ack):
    ack()


def execute():
    pass
