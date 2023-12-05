<script lang="ts">
	import { onMount } from 'svelte';
	import io, { Socket } from 'socket.io-client';
	import Title from './title.svelte';
	import Score from './score.svelte';

	let socket: Socket;
	let gameMode = 0;
	let score1 = 0;
	let score2 = 0;
	let initialCountdownMs: number;
	let interval: number;

	onMount(() => {
		// Connect to the backend
		socket = io(`127.0.0.1:5000`); // Replace with your backend URL

		// Example event listener
		socket.on('SCORE', (data) => {
			score1 = data.score1;
			score2 = data.score2;
		});

		socket.on('GAME_MODE', (data) => {
			gameMode = +data.gameMode;
		});

		socket.on('GAME_ACTIVE', (data) => {
			initialCountdownMs = data.gameMs;
		});
	});

	$: countdownMs = initialCountdownMs;

	$: if (initialCountdownMs) {
		clearInterval(interval);
		interval = setInterval(() => {
			countdownMs -= 1000;

			if (countdownMs <= 0) {
				clearInterval(interval);
				countdownMs = 0;
			}
		}, 1000);
	}
</script>

<Title {countdownMs} {gameMode} />
<Score {score1} {score2} {gameMode} />
