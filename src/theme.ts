import {continueRender, delayRender, useCurrentFrame, useVideoConfig} from 'remotion';
import {ANTON_WOFF2, MONT_WOFF2} from './fontData';

export const anton = 'Anton';
export const mont = 'Montserrat';

// Plain @font-face from embedded data URLs. The render waits (max 5s) for the
// faces to be ready, but never blocks forever if the browser doesn't report back.
if (typeof document !== 'undefined' && !document.getElementById('bi-fonts')) {
	const style = document.createElement('style');
	style.id = 'bi-fonts';
	style.textContent = `
@font-face{font-family:'Anton';src:url(${ANTON_WOFF2}) format('woff2');font-weight:400;font-display:block}
@font-face{font-family:'Montserrat';src:url(${MONT_WOFF2}) format('woff2');font-weight:100 900;font-display:block}`;
	document.head.appendChild(style);
	const handle = delayRender('Loading embedded fonts', {timeoutInMilliseconds: 30000});
	Promise.race([
		Promise.all([document.fonts.load('400 40px Anton'), document.fonts.load('900 40px Montserrat')]),
		new Promise((r) => setTimeout(r, 5000)),
	]).finally(() => continueRender(handle));
}

export const FPS = 60;
// All animation timings are authored in 30fps "beats"; this maps any render fps onto them.
export const BASE_FPS = 30;
export const useF = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	return frame / (fps / BASE_FPS);
};
export const useR = () => useVideoConfig().fps / BASE_FPS;
export const W = 1080;
export const H = 1920;

// TikTok + IG Reels safe zone (union of both UIs, 1080x1920)
export const SAFE = {top: 250, bottom: 1500, left: 60, right: 910};

// Product sits roughly y 570–1410 in this footage. Graphics live above or below it.
export const ZONE_TOP = {y: 270, h: 290}; // car bonnet area
export const ZONE_LOW = {y: 1400, h: 100}; // forearm / ground area, above platform UI

export const C = {
	ice: '#9BE8FF',
	iceDeep: '#2FB8FF',
	white: '#FFFFFF',
	black: '#05080C',
	yellow: '#FFD21F',
	red: '#FF2D46',
};
