from app.data import character_photo


class CardCharacters:
    def __init__(self, ident, player_nick_name, universe, cb, name, slave, rid, data,
                 status="🎴", avatar=None, avatar_type=None, rarity=None, strength=None,
                 agility=None, intelligence=None, clas=None, shield=0, stun=0, health=None,
                 attack=None, defense=None, mana=None, crit_dmg=None, crit_ch=None,
                 round=1, turn=True, c_status="🎴", is_active=False):

        # Если переданы None, получаем данные из character_photo
        if avatar is None:
            avatar = character_photo.get_stats(universe, name, 'avatar')
        if avatar_type is None:
            avatar_type = character_photo.get_stats(universe, name, 'type')
        if rarity is None:
            rarity = character_photo.get_stats(universe, name, 'rarity')
        if strength is None:
            strength = character_photo.get_stats(universe, name, 'arena')['strength']
        if agility is None:
            agility = character_photo.get_stats(universe, name, 'arena')['agility']
        if intelligence is None:
            intelligence = character_photo.get_stats(universe, name, 'arena')['intelligence']
        if clas is None:
            clas = character_photo.get_stats(universe, name, 'arena')['class']

        # Устанавливаем параметры объекта
        self.status = status
        self.avatar = avatar
        self.avatar_type = avatar_type
        self.ident = ident
        self.player_nick_name = player_nick_name
        self.universe = universe
        self.cb = cb
        self.rarity = rarity
        self.name = name
        self.strength = strength
        self.agility = agility
        self.intelligence = intelligence
        self.shield = shield
        self.stun = stun
        self.health = health if health is not None else strength * 75
        self.attack = attack if attack is not None else strength * 5 + agility * 5 + intelligence * 5
        self.defense = defense if defense is not None else (strength + agility + (intelligence // 2)) // 4
        self.mana = mana if mana is not None else intelligence * 10
        self.crit_dmg = crit_dmg if crit_dmg is not None else strength + (agility // 2) + (intelligence // 4)
        self.crit_ch = crit_ch if crit_ch is not None else agility + (strength // 2) + (intelligence // 4)
        self.clas = clas
        self.round = round
        self.turn = turn
        self.rid = rid
        self.slave = slave
        self.c_status = c_status
        self.data = data
        self.is_active = is_active
