import json
import logging
import asyncio

logger = logging.getLogger('DiscordBot')

class DataManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.lock = asyncio.Lock()

    async def load_data(self):
        async with self.lock:
            try:
                with open(self.data_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning("Fichier de données vide, création d'une nouvelle structure")
                        return {"config": {}, "stats": {}}
                    return json.loads(content)
            except FileNotFoundError:
                logger.warning(f"Fichier {self.data_file} non trouvé, création d'une nouvelle structure")
                return {"config": {}, "stats": {}}
            except json.JSONDecodeError:
                logger.error(f"Erreur de décodage JSON dans {self.data_file}. Voulez vous créer une nouvelle structure ? Toutes les données du bot seront perdues (O/N)")
                response = input()
                if response.lower() in ['o', 'oui', 'y', 'yes']:
                    return {"config": {}, "stats": {}}
                else:
                    logger.error("Arrêt du bot")
                    exit(1)

    async def save_data(self, data):
        async with self.lock:
            try:
                with open(self.data_file, 'w') as f:
                    json.dump(data, f, indent=4)
                logger.debug("Données sauvegardées avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde des données: {e}")

    async def get_guild_config(self, guild_id: str) -> dict:
        data = await self.load_data()
        if guild_id not in data['config']:
            data['config'][guild_id] = {
                "send_public": True,
                "send_message": True,
                "enable_reactions": True
            }
            await self.save_data(data)
        return data['config'][guild_id]

    async def update_stats(self, guild_id: str, user_id: str, stat: str):
        data = await self.load_data()
        if guild_id not in data['stats']:
            data['stats'][guild_id] = {}
        if user_id not in data['stats'][guild_id]:
            data['stats'][guild_id][user_id] = {'count_69': 0}
        
        data['stats'][guild_id][user_id][stat] += 1
        await self.save_data(data)