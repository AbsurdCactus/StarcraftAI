import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *  # I need to reference a nexus to use it


class ClayBot(sc2.BotAI):

    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_army_buildings()
        await self.build_offensive_army()

        # await self.expand()

    async def build_workers(self):
        for nexus in self.townhalls(
                UnitTypeId.NEXUS).ready.idle:  # there is no need to add to queue since bot can react instantaneously
            if self.can_afford(UnitTypeId.PROBE):  # had to change to unit typeID
                self.do(nexus.train(UnitTypeId.PROBE))

    async def build_pylons(self):  # you need to pass 'self' for this
        nexusp = self.townhalls(UnitTypeId.NEXUS).ready
        if nexusp.exists:
            cc = nexusp.first
            if self.supply_left < 5 and not self.already_pending(UnitTypeId.PYLON):
                if self.can_afford(UnitTypeId.PYLON):
                    await self.build(UnitTypeId.PYLON, near=nexusp.first)  # if you want to, you could put a machine
                    # learning algorithm
                    # to this function right here. Example: where should the AI PLACE the pylon?

                    '''if self.supply_left < 5 and not self.already_pending(UnitTypeId.PYLON):
                                nexuses = self.units(UnitTypeId.NEXUS).ready
                                if nexuses.exists:
                                    if self.can_afford(UnitTypeId.PYLON):
                                        await self.build(UnitTypeId.PYLON, near=nexuses.first)  # if you want to, you could put a machine
                                        # learning algorithm
                                        # to this function right here. Example: where should the AI PLACE the pylon?'''

    async def build_assimilators(self):
        for nexus in self.townhalls(UnitTypeId.NEXUS).ready:
            vgs = self.vespene_geyser.closer_than(15, nexus)
            for vg in vgs:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vg.position)
                if worker is None:
                    break
                if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                    self.do(worker.build(ASSIMILATOR, vg), subtract_cost=True)
                    self.do(worker.stop(queue=True))

        '''for nexus in self.townhalls(UnitTypeId.NEXUS).ready:
            vaspenes = self.state..closer_than(25.0, nexus)#any geysers within 20 units of our nexus
            for vaspene in vaspenes:
                if not self.can_afford(UnitTypeId.ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)#assigning workers to the assimilator
                if worker is None:
                    break
                if not self.units(UnitTypeId.ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(UnitTypeId.ASSIMILATOR, vaspene))'''

    async def expand(self):
        if self.townhalls.ready.amount + self.already_pending(NEXUS) < 3:
            if self.can_afford(NEXUS):
                await self.expand_now()

        '''if self.units(UnitTypeId.NEXUS).amount < 3 and self.can_afford(UnitTypeId.NEXUS):
            await self.expand_now()'''

    async def offensive_army_buildings(self):
        '''if self.townhalls(UnitTypeId.PYLON).ready.exists:
            pylon = self.townhalls(UnitTypeId.PYLON).ready.random
            if self.townhalls(UnitTypeId.GATEWAY).ready.exists:
                if not self.townhalls(UnitTypeId.CYBERNETICSCORE):
                    if self.can_afford(UnitTypeId.CYBERNETICSCORE) and not self.already_pending(
                            UnitTypeId.CYBERNETICSCORE):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=pylon)
            else:
                if self.can_afford(UnitTypeId.GATEWAY) and not self.already_pending(UnitTypeId.GATEWAY):
                    await self.build(UnitTypeId.GATEWAY, near=pylon)'''
        if self.structures(PYLON).ready:
            proxy = self.structures(PYLON).closest_to(self.enemy_start_locations[0])
            pylon = self.structures(PYLON).ready.random
            if self.structures(GATEWAY).ready:
                # If we have no cyber core, build one
                if not self.structures(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and self.already_pending(CYBERNETICSCORE) == 0:
                        await self.build(CYBERNETICSCORE, near=pylon)
            # Build up to 4 gates
            if self.can_afford(GATEWAY) and self.structures(WARPGATE).amount + self.structures(GATEWAY).amount < 4:
                await self.build(GATEWAY, near=pylon)

    async def build_offensive_army(self,proxy):# TODO fix this function
        '''for gw in self.structures(GATEWAY).ready.idle:
            if self.can_afford(STALKER) and self.supply_left > 0:
                await self.build(gw.train(STALKER))'''


        for warpgate in self.structures(GATEWAY).ready:
            abilities = await self.get_available_abilities()
            # all the units have the same cooldown anyway so let's just look at ZEALOT
            if AbilityId.GATEWAYTRAIN_STALKER in abilities:
                pos = proxy.position.to2.random_on_distance(4)
                placement = await self.find_placement(AbilityId.GATEWAYTRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    # return ActionResult.CantFindPlacementLocation
                    print("can't place")
                    return
                self.do(warpgate.warp_in(STALKER, placement), subtract_cost=True, subtract_supply=True)


run_game(maps.get("AcropolisLE"), [
    Bot(Race.Protoss, ClayBot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=False)
