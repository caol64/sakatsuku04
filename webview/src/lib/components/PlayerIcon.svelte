<script lang="ts">
    import Airplane from "$lib/icons/Airplane.svelte";
    import Avatar from "$lib/icons/Avatar.svelte";
    import Football from "$lib/icons/Football.svelte";
    import type { TeamPlayer } from "$lib/models";
    import { getTeamData } from "$lib/utils";
    import HStack from "./Stack/HStack.svelte";
    import Tooltip from "./Tooltip.svelte";

    let { teamPlayer } : { teamPlayer: TeamPlayer } = $props();
</script>

<HStack className="items-center">
    <div class="mr-2 w-3.5 h-3.5 flex items-center justify-center">
        {#if teamPlayer.bringAbroads && teamPlayer.bringAbroads.length > 0}
            {@const tooltipText = teamPlayer.bringAbroads
                .map(i => {
                    const isOver = i > 1000;
                    const index = isOver ? i - 1000 : i;
                    const name = getTeamData()[index - 255];
                    return isOver ? `${name}(C)` : name;
                })
                .join("<br>")}
            <Tooltip text={tooltipText} width="100px">
                <Airplane />
            </Tooltip>
        {/if}
    </div>
    <div class="mr-2 w-3.5 h-3.5 flex items-center justify-center">
        {#if teamPlayer.scouts && teamPlayer.scouts.length > 0}
            {@const tooltipText = `${teamPlayer.scouts.join("<br>")}`}
            <Tooltip text={tooltipText} width="100px">
                <Avatar />
            </Tooltip>
        {/if}
    </div>

    <div class="mr-2 w-3.5 h-3.5 flex items-center justify-center">
        {#if teamPlayer.albumType !== 0}
            {@const tooltipText = `${teamPlayer.albumType === 1 ? "已获得" : "未获得"}`}
            <Tooltip text={tooltipText} width="70px">
                <Football />
            </Tooltip>
        {/if}
    </div>
</HStack>
