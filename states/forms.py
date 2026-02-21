from aiogram.fsm.state import State, StatesGroup


class FinderForm(StatesGroup):
    """FSM states for Finder (found an item) flow."""
    category = State()
    name = State()
    photo = State()
    signs = State()
    where_found = State()
    location = State()
    confirm = State()


class LoserForm(StatesGroup):
    """FSM states for Loser (lost an item) flow."""
    name = State()
    signs = State()
    photo = State()
    confirm = State()
