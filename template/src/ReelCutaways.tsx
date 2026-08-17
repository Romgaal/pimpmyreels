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

export const ReelCutaways: React.FC = () => {
	const segs = mapping.segments as Seg[];
	const top = (mapping as {imageTop?: number}).imageTop ?? 235;
	const shadow = (mapping as {imageShadow?: boolean}).imageShadow === true;
	return (
		<AbsoluteFill style={{backgroundColor: '#000'}}>
			<OffthreadVideo src={staticFile(mapping.rush)} />
			{segs.map((seg, i) => {
				const end = seg.end ?? segs[i + 1]?.start ?? mapping.durationInFrames;
				return (
					<Sequence key={i} from={seg.start} durationInFrames={end - seg.start}>
						{seg.type === 'collage' ? (
							<Collage images={seg.images as string[]} />
						) : (
							<ImgCut seg={seg} top={top} shadow={shadow} />
						)}
					</Sequence>
				);
			})}
		</AbsoluteFill>
	);
};
