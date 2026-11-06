"""
FSM (finite state machine) states.

A state remembers "which question the bot is waiting an answer for",
so the bot knows how to treat the next message from the user.
"""
from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    """Customer checkout: name -> phone -> address -> comment -> confirmation."""
    name = State()
    phone = State()
    address = State()
    comment = State()
    confirm = State()


class AddProduct(StatesGroup):
    """Admin: adding a new product step by step."""
    category = State()
    name = State()
    description = State()
    price = State()
    photo = State()


class Broadcast(StatesGroup):
    """Admin: sending a message to every user."""
    message = State()
    confirm = State()
