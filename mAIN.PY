import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from config import TOKEN
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "u11_tg_admin.settings")
django.setup()

from bot.models import Step

bot = Bot(TOKEN)
dp = Dispatcher()
rg = Router()

class States(StatesGroup):
    start_menu = State()
    start_fill_form = State()

@rg.message(Command("start"))
async def start(message:types.Message, state:FSMContext):
    await state.set_state(States.start_menu)
    data = await state.get_state()
    # steps = await sync_to_async(Step.objects.first)()
    steps = Step.objects.select_related('keyboard').prefetch_related('keyboard__buttons__content_type').all()
    async_list = sync_to_async(list)
    steps_list = await async_list(steps)
    for st in steps_list:
        await message.answer(text=st.step_num)
        if st.keyboard is not None:
            await message.answer(text=st.keyboard.title)
            buttons = await sync_to_async(lambda: list(st.keyboard.buttons.all()))()
            if buttons:
                await message.answer(text=f"Buttons: {buttons[0]}")
                for button in buttons:
                    target_object = await sync_to_async(lambda: button.target)()
                    if target_object:
                        await message.answer(text=f"Button '{button.label}' связана с: {target_object}")
                    else:
                        await message.answer(text=f"Button '{button.label}' не связана ни с чем")

            else:
                await message.answer(text="No buttons in keyboard")
        else:
            await message.answer(text="No keyboard")

@rg.message(States.start_menu)
async def check_menu_buttons(message:types.Message, state:FSMContext):
    await state.set_state(States.start_fill_form)



dp.include_router(rg)

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
