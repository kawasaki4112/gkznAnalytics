import io
import qrcode
from typing import Optional
from aiogram import Bot
from aiogram.types import BufferedInputFile, Message

from src.data.repositories.specialist_repository import specialist_crud


async def generate_and_upload_qr(bot: Bot, specialist_id: str, link: str, admin_chat_id: int) -> Optional[str]:
    """
    Генерирует QR-код из ссылки, загружает его в Telegram и возвращает file_id.
    
    Args:
        bot: Экземпляр бота
        specialist_id: ID специалиста
        link: Ссылка для QR-кода
        admin_chat_id: ID чата администратора для загрузки фото
        
    Returns:
        file_id загруженного фото или None в случае ошибки
    """
    try:
        # Генерируем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(link)
        qr.make(fit=True)

        # Создаем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем в BytesIO
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        
        # Создаем BufferedInputFile для отправки
        photo = BufferedInputFile(bio.read(), filename=f"qr_{specialist_id}.png")
        
        # Отправляем фото в невидимый канал или удаляем сразу после получения file_id
        # Используем того же админа для загрузки
        message = await bot.send_photo(
            chat_id=admin_chat_id,
            photo=photo
        )
        
        # Получаем file_id самого большого фото
        file_id = message.photo[-1].file_id
        
        # Удаляем сообщение с QR-кодом
        await message.delete()
        
        # Обновляем запись специалиста
        await specialist_crud.update(
            filters={"id": specialist_id},
            updates={"qr": file_id}
        )
        
        return file_id
        
    except Exception as e:
        print(f"Ошибка при генерации QR-кода для специалиста {specialist_id}: {e}")
        return None


async def generate_qr_for_specialists(bot: Bot, specialist_ids: list[str], admin_chat_id: int):
    """
    Фоновая генерация QR-кодов для списка специалистов с отображением прогресса.
    
    Args:
        bot: Экземпляр бота
        specialist_ids: Список ID специалистов
        admin_chat_id: ID чата администратора
    """
    if not specialist_ids:
        return
    
    total = len(specialist_ids)
    success = 0
    failed = 0
    
    # Отправляем начальное сообщение
    status_message = await bot.send_message(
        chat_id=admin_chat_id,
        text=f"🔄 <b>Генерация QR-кодов</b>\n\n"
             f"Обработано: 0/{total}\n"
             f"✅ Успешно: 0\n"
             f"❌ Ошибок: 0",
        parse_mode="HTML"
    )
    
    for idx, spec_id in enumerate(specialist_ids, 1):
        specialist = await specialist_crud.get(id=spec_id)
        if specialist and specialist.link and not specialist.qr:
            result = await generate_and_upload_qr(bot, spec_id, specialist.link, admin_chat_id)
            if result:
                success += 1
            else:
                failed += 1
        
        # Обновляем сообщение каждые 3 специалиста или в конце
        if idx % 3 == 0 or idx == total:
            try:
                await status_message.edit_text(
                    f"🔄 <b>Генерация QR-кодов</b>\n\n"
                    f"Обработано: {idx}/{total}\n"
                    f"✅ Успешно: {success}\n"
                    f"❌ Ошибок: {failed}",
                    parse_mode="HTML"
                )
            except:
                pass  # Игнорируем ошибки редактирования
    
    # Финальное сообщение
    await status_message.edit_text(
        f"✅ <b>Генерация QR-кодов завершена</b>\n\n"
        f"Всего: {total}\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {failed}",
        parse_mode="HTML"
    )
