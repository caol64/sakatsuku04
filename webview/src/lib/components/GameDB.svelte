<script lang="ts">
    import { setGameVersion, setModeState } from "$lib/globalState.svelte";
    import Forward from "$lib/icons/Forward.svelte";

    async function gotoPlayerDB() {
        setModeState("bPlayerView");
        setGameVersion(1);
    }

    async function gotoCoachDB() {
        setModeState("bCoachView");
        setGameVersion(1);
    }

    async function gotoScoutDB() {
        setModeState("bScoutView");
        setGameVersion(1);
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
        <div class="flex items-center space-x-2 text-sm">
            <button onclick={ gotoPlayerDB } class="text-blue-600 cursor-pointer flex items-center">
                球员数据库
                <Forward />
            </button>
        </div>
        <div class="flex items-center space-x-2 text-sm">
            <button onclick={ gotoCoachDB } class="text-blue-600 cursor-pointer flex items-center">
                教练数据库
                <Forward />
            </button>
        </div>
        <div class="flex items-center space-x-2 text-sm">
            <button onclick={ gotoScoutDB } class="text-blue-600 cursor-pointer flex items-center">
                球探数据库
                <Forward />
            </button>
        </div>
    </div>
</div>
