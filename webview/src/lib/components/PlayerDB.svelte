<script lang="ts">
    import { setModeState } from "$lib/globalState.svelte";

    async function gotoPlayerDB() {
        setModeState("bPlayerView");
    }
</script>

<div class="flex items-center justify-center space-x-20 w-full">
    <div class="text-gray-500 dark:text-gray-300 text-6xl">
        <svg width="40" height="40" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M32 6H22V42H32V6Z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>
            <path d="M42 6H32V42H42V6Z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>
            <path d="M10 6L18 7L14.5 42L6 41L10 6Z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>
            <path d="M37 18V15" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M27 18V15" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <div class="flex flex-col space-y-2">
        <p class="text-gray-700 dark:text-gray-300 text-base font-medium">
            球员数据库
        </p>
        <div class="flex items-center space-x-2 text-sm">
            <button onclick={ gotoPlayerDB } class="text-blue-600 cursor-pointer flex items-center">
                进入
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </button>
        </div>
    </div>
</div>
