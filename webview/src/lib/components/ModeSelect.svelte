<script lang="ts">
    import VStack from "$lib/components/Stack/VStack.svelte";
    import SaveFileSelect from "./SaveFileSelect.svelte";
    import Pcsx2Connect from "./Pcsx2Connect.svelte";
    import { onMount } from "svelte";
    import About from "./About.svelte";

    onMount(async () => {
        if (window.pywebview?.api?.reset) {
            await window.pywebview.api.reset();
        }
    });
</script>

<VStack className="flex flex-col items-center justify-center h-full w-full">
    <div class="absolute top-4 right-2">
        <About />
    </div>
    <div class="flex justify-between space-x-8 w-11/12">
        <div class="flex-1 border border-dashed border-gray-300 rounded-md p-28 flex items-center justify-between">
            <SaveFileSelect />
        </div>

        <div class="flex-1 border border-dashed border-gray-300 rounded-md p-28 flex items-center justify-between">
            <Pcsx2Connect />
        </div>
    </div>
</VStack>

<style lang="postcss">
    @reference "tailwindcss";
</style>
