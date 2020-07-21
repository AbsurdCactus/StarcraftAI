import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from sc2.units import Units
from sc2.unit import Unit
from sc2.position import Point2
from sc2.ids.unit_typeid import UnitTypeId



class ClayBot(sc2.BotAI):
    async def on_step(self, iteration):
        # what to do every step
        await self.distribute_workers()  # in sc2/bot_ai.py
        await self.assemble_workers()

    # TODO: figure out how to multi-manage command centers.
    async def assemble_workers(self):
        for command_center in self.units(UnitTypeId.COMMANDCENTER).ready.idle:
            if self.can_afford(UnitTypeId.SCV) and self.supply_workers < 16:
                await self.do(command_center.train(UnitTypeId.SCV))

        

# Ephemeron is default map.
run_game(maps.get("EphemeronLE"), [
    Bot(Race.Terran, ClayBot()),
    Computer(Race.Zerg, Difficulty.Easy)
], realtime=False)