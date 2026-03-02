from app.data import mongodb


async def rerank(rank: int | None) -> str:
    rank = rank or 1
    if rank == 1:
        return '🎖️'
    elif rank == 2:
        return '🎖️🎖️'
    elif rank == 3:
        return '🎖️🎖️🎖️'
    elif rank >= 4:
        return '🎖️🎖️🎖️🎖️'
    return '🎖️'  # fallback


async def rerank_battle(rank: int | None) -> str:
    return await rerank(rank)


async def update_rank(user_id: int, wins: int | None) -> None:
    wins = wins or 0
    if wins >= 600:
        rank = 4
    elif wins >= 300:
        rank = 3
    elif wins >= 100:
        rank = 2
    else:
        rank = 1
    await mongodb.update_user(user_id, {'stats.rank': rank})


async def level(lvl: int | None) -> str:
    lvl = lvl or 1
    lvl = min(max(lvl, 1), 7)
    return f'level {lvl}'


async def update_level(user_id: int, count: int | None) -> None:
    count = count or 0
    if count >= 85:
        level_value = 7
    elif count >= 70:
        level_value = 6
    elif count >= 55:
        level_value = 5
    elif count >= 40:
        level_value = 4
    elif count >= 25:
        level_value = 3
    elif count >= 10:
        level_value = 2
    else:
        level_value = 1
    await mongodb.update_user(user_id, {'campaign.level': level_value})
