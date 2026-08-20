import React from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, staticFile} from 'remotion';
import {Gif} from '@remotion/gif';
import mapping from '../mapping.json';

// Style rules baked in (see skills/pimp/references/style-rules.md):
// hard cuts only — NO transitions, NO zoom, NO shadow, NO text overlays.
type Seg = {
	start: number;
	end?: number;
	type?: string;
	image?: string;
	images?: string[];
	format?: string;
	align?: string;
};

const Media: React.FC<{src: string; style: React.CSSProperties}> = ({src, style}) =>
	src.toLowerCase().endsWith('.gif') ? (
		<Gif src={staticFile(src)} style={style} fit="cover" />
	) : (
		<Img src={staticFile(src)} style={style} />
	);

// Burned-in captions (Captions app etc.) sometimes sit HIGH, inside the cutaway band.
// `captionsTop` in mapping.json declares where they start; every overlay is then fitted
// above them instead of covering the first words. Measure it, never guess it:
// `python3 scripts/detect_captions.py <project>`.
const capTop = (mapping as {captionsTop?: number}).captionsTop;
// Purely visual breathing room. The sampling slack is already baked into captionsTop
// by detect_captions.py, which reports a conservative bound, not a raw measurement.
const GAP = 10;

const ImgCut: React.FC<{seg: Seg; top: number; shadow: boolean}> = ({seg, top, shadow}) => {
	// Square is the default: the reference format keeps every cutaway consistent.
	// 'landscape' is the justified exception (wide compositions that a square crop would destroy).
	const fmt = seg.format ?? (mapping as {imageFormat?: string}).imageFormat;
	const square = fmt !== 'landscape';
	let w = square ? Math.round(mapping.width * 0.41) : Math.round(mapping.width * 0.519);
	let h = square ? w : Math.round(w * 0.575);
	// Shrink (keeping the aspect ratio) so the image never enters the caption band.
	if (capTop && top + h > capTop - GAP) {
		const k = (capTop - GAP - top) / h;
		h = Math.round(h * k);
		w = Math.round(w * k);
	}
	const justify =
		seg.align === 'left' ? 'flex-start' : seg.align === 'right' ? 'flex-end' : 'center';
	return (
		<div
			style={{
				position: 'absolute',
				top,
				left: 0,
				right: 0,
				display: 'flex',
				justifyContent: justify,
				// Asymmetric on purpose: the platform icon rail eats ~140px on the RIGHT.
				// 64px was fine on the left and overflowed on the right (measured).
				paddingLeft: seg.align === 'left' ? 64 : 0,
				paddingRight: seg.align === 'right' ? 150 : 0,
			}}
		>
			<div
				style={{
					width: w,
					height: h,
					borderRadius: 4,
					overflow: 'hidden',
					boxShadow: shadow ? '0 10px 28px rgba(0,0,0,.28)' : undefined,
				}}
			>
				<Media
					src={seg.image as string}
					style={{width: '100%', height: '100%', objectFit: 'cover'}}
				/>
			</div>
		</div>
	);
};

const COLLAGE_TOP = 44;

const Collage: React.FC<{images: string[]}> = ({images}) => {
	// 3x2 square cells: height = 2 cells + 1 gap. Narrow it if burned captions sit high.
	let pct = 0.68;
	if (capTop) {
		const cell = (mapping.width * pct - 8) / 3;
		const hgt = cell * 2 + 4;
		if (COLLAGE_TOP + hgt > capTop - GAP) {
			pct *= (capTop - GAP - COLLAGE_TOP) / hgt;
		}
	}
	return (
	<div
		style={{
			position: 'absolute',
			top: COLLAGE_TOP,
			left: `${(100 - pct * 100) / 2}%`,
			width: `${pct * 100}%`,
			display: 'grid',
			gridTemplateColumns: 'repeat(3, 1fr)',
			gap: 4,
		}}
	>
		{images.slice(0, 6).map((im, i) => (
			<div
				key={i}
				style={{aspectRatio: '1', borderRadius: 4, overflow: 'hidden'}}
			>
				<Media src={im} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
			</div>
		))}
	</div>
	);
};

// The intro collage IS the hook. Cutting to the first cutaway after a beat or two
// throws away the visual that stops the scroll, so the collage holds for at least
// this long and any cutaway underneath it is clipped or dropped — enforced here
// rather than left to whoever writes the timings.
const COLLAGE_MIN_SECONDS = 3;
// A cutaway clipped down to a fraction of a second reads as a glitch, not an edit.
// Below this, drop it and let the NEXT one start when the collage ends — no flash,
// and no hole between the collage and the first real image.
const MIN_CUT_SECONDS = 1;

export const ReelCutaways: React.FC = () => {
	const segs = mapping.segments as Seg[];
	const top = (mapping as {imageTop?: number}).imageTop ?? 235;
	const shadow = (mapping as {imageShadow?: boolean}).imageShadow === true;
	const minS = (mapping as {collageMinSeconds?: number}).collageMinSeconds ?? COLLAGE_MIN_SECONDS;
	const {fps, durationInFrames} = mapping;

	// Resolve the timeline once, then render it. Doing this inside the render loop is
	// how the first version left a hole: dropping a clipped cutaway is only half the
	// job — the next one has to take its place at the collage's end.
	const hasCollage = segs[0]?.type === 'collage';
	const collageEnd = hasCollage
		? Math.max(segs[1]?.start ?? durationInFrames, segs[0].start + Math.round(minS * fps))
		: 0;

	const items: {from: number; end: number; seg: Seg; collage?: boolean}[] = [];
	if (hasCollage) items.push({from: segs[0].start, end: collageEnd, seg: segs[0], collage: true});

	let firstAfterCollage = true;
	for (let i = hasCollage ? 1 : 0; i < segs.length; i++) {
		const seg = segs[i];
		const rawEnd = seg.end ?? segs[i + 1]?.start ?? durationInFrames;
		if (rawEnd <= collageEnd) continue;                       // entirely under the collage
		let from = Math.max(seg.start, collageEnd);
		if (firstAfterCollage) {
			// Whichever cutaway comes first takes over the instant the collage ends —
			// no gap. But not if the clip leaves it under a second: that reads as a
			// glitch, so skip it and hand the slot to the next one.
			if (seg.start < collageEnd && rawEnd - collageEnd < MIN_CUT_SECONDS * fps) continue;
			from = collageEnd;
			firstAfterCollage = false;
		}
		items.push({from, end: rawEnd, seg});
	}

	return (
		<AbsoluteFill style={{backgroundColor: '#000'}}>
			<OffthreadVideo src={staticFile(mapping.rush)} />
			{items.map((it, i) => (
				<Sequence key={i} from={it.from} durationInFrames={it.end - it.from}>
					{it.collage ? (
						<Collage images={it.seg.images as string[]} />
					) : (
						<ImgCut seg={it.seg} top={top} shadow={shadow} />
					)}
				</Sequence>
			))}
		</AbsoluteFill>
	);
};
