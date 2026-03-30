try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
except Exception:
    plt = None
    FigureCanvasAgg = None
import itertools
import re
import os
import threading
import importlib
import importlib.util
import io
import html
import webbrowser

try:
    import numpy as np
except Exception:
    np = None

if importlib.util.find_spec("flask") is not None:
    flask_mod = importlib.import_module("flask")
    Flask = flask_mod.Flask
    jsonify = flask_mod.jsonify
    request = flask_mod.request
    Response = flask_mod.Response
    send_file = flask_mod.send_file
else:
    Flask = None
    jsonify = None
    request = None
    Response = None
    send_file = None

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception:
    tk = None
    ttk = None

if importlib.util.find_spec("simpleaudio") is not None:
    sa = importlib.import_module("simpleaudio")
else:
    sa = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None



class GuitarChords:
    AUDIO_SAMPLE_RATE = 44100
    PAGE_SIZE = 8
    MAX_UI_SHAPES = 48
    MAX_UI_DPI = 280
    MAX_EXPORT_DPI = 480
    GUITAR_SAMPLE_MIDI = 36

    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    DISPLAY_NOTE_NAMES = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]

    NOTE_MAP = {
        "C":0,"C#":1,"Db":1,"D":2,"D#":3,"Eb":3,"E":4,
        "F":5,"F#":6,"Gb":6,"G":7,"G#":8,"Ab":8,
        "A":9,"A#":10,"Bb":10,"B":11
    }

    CHORD_FORMULAS = {
        "major": [0, 4, 7],
        "minor": [0, 3, 7],
        "dim": [0, 3, 6],
        "aug": [0, 4, 8],
        "power5": [0, 7],
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
        "six": [0, 4, 7, 9],
        "m6": [0, 3, 7, 9],
        "maj7": [0, 4, 7, 11],
        "m7": [0, 3, 7, 10],
        "dom7": [0, 4, 7, 10],
        "dim7": [0, 3, 6, 9],
        "m7b5": [0, 3, 6, 10],
        "mmaj7": [0, 3, 7, 11],
        "add9": [0, 4, 7, 2],
        "madd9": [0, 3, 7, 2],
        "six9": [0, 4, 7, 9, 2],
        "dom9": [0, 4, 7, 10, 2],
        "maj9": [0, 4, 7, 11, 2],
        "m9": [0, 3, 7, 10, 2],
        "dom11": [0, 4, 7, 10, 2, 5],
        "maj11": [0, 4, 7, 11, 2, 5],
        "m11": [0, 3, 7, 10, 2, 5],
        "dom13": [0, 4, 7, 10, 2, 5, 9],
        "maj13": [0, 4, 7, 11, 2, 5, 9],
        "m13": [0, 3, 7, 10, 2, 5, 9],
        "seven_sus4": [0, 5, 7, 10],
        "seven_sus2": [0, 2, 7, 10],
        "seven_b5": [0, 4, 6, 10],
        "seven_sharp5": [0, 4, 8, 10],
        "seven_b9": [0, 4, 7, 10, 1],
        "seven_sharp9": [0, 4, 7, 10, 3],
        "seven_sharp11": [0, 4, 7, 10, 6],
        "seven_b13": [0, 4, 7, 10, 8],
        "nine_sus4": [0, 5, 7, 10, 2],
        "add11": [0, 4, 7, 5],
        "add13": [0, 4, 7, 9],
        "madd11": [0, 3, 7, 5],
        "madd13": [0, 3, 7, 9],
        "alt": [0, 4, 10, 1, 3, 6, 8],
    }

    CHORD_ALIASES = {
        "": "major",
        "maj": "major",
        "m": "minor",
        "min": "minor",
        "-": "minor",
        "dim": "dim",
        "o": "dim",
        "aug": "aug",
        "+": "aug",
        "5": "power5",
        "sus": "sus4",
        "sus2": "sus2",
        "sus4": "sus4",
        "6": "six",
        "m6": "m6",
        "maj7": "maj7",
        "m7": "m7",
        "min7": "m7",
        "7": "dom7",
        "dim7": "dim7",
        "o7": "dim7",
        "m7b5": "m7b5",
        "min7b5": "m7b5",
        "half-dim": "m7b5",
        "mmaj7": "mmaj7",
        "minmaj7": "mmaj7",
        "mmaj": "mmaj7",
        "add9": "add9",
        "madd9": "madd9",
        "6/9": "six9",
        "69": "six9",
        "9": "dom9",
        "maj9": "maj9",
        "m9": "m9",
        "11": "dom11",
        "maj11": "maj11",
        "m11": "m11",
        "13": "dom13",
        "maj13": "maj13",
        "m13": "m13",
        "7sus4": "seven_sus4",
        "7sus2": "seven_sus2",
        "7b5": "seven_b5",
        "7#5": "seven_sharp5",
        "7b9": "seven_b9",
        "7#9": "seven_sharp9",
        "7#11": "seven_sharp11",
        "7b13": "seven_b13",
        "9sus4": "nine_sus4",
        "add11": "add11",
        "add13": "add13",
        "madd11": "madd11",
        "madd13": "madd13",
        "7alt": "alt",
        "alt": "alt",
    }

    # Universal major-shape frames used as positional windows.
    FRAME_SKELETONS = [
        ("C", (-1, 3, 2, 0, 1, 0), "C"),
        ("A", (-1, 0, 2, 2, 2, 0), "A"),
        ("G", (3, 2, 0, 0, 0, 3), "G"),
        ("E", (0, 2, 2, 1, 0, 0), "E"),
        ("D", (-1, -1, 0, 2, 3, 2), "D"),
    ]

    def __init__(self, tuning=None, max_fret=12):
        self.tuning = tuning or [40, 45, 50, 55, 59, 64]
        self.max_fret = max_fret

    def parse_chord(self, chord_name):
        info = self._parse_chord_info(chord_name)
        return info["chord_notes"]

    def _parse_chord_info(self, chord_name):
        # Support slash chords by parsing the harmony before '/'.
        chord_name = chord_name.strip()
        parts = chord_name.split("/")
        chord_core = parts[0]
        bass_name = parts[1] if len(parts) > 1 else None
        match = re.match(r"^([A-Ga-g])([#b]?)(.*)$", chord_core)
        if not match:
            raise ValueError(f"Invalid chord name: {chord_name}")

        root_letter, accidental, quality = match.groups()
        root = root_letter.upper() + accidental
        if root not in self.NOTE_MAP:
            raise ValueError(f"Unsupported root note: {root}")

        normalized_quality = quality.strip().replace(" ", "")
        normalized_quality = normalized_quality.replace("(", "").replace(")", "")
        normalized_quality = normalized_quality.lower()

        canonical = self.CHORD_ALIASES.get(normalized_quality)
        if canonical is None:
            raise ValueError(
                f"Unsupported chord type: {quality or '(major)'}"
            )

        formula = self.CHORD_FORMULAS[canonical]
        root_pc = self.NOTE_MAP[root]
        chord_notes = [(root_pc + i) % 12 for i in formula]

        bass_pc = None
        if bass_name:
            bass_name = bass_name[0].upper() + bass_name[1:]
            if bass_name not in self.NOTE_MAP:
                raise ValueError(f"Unsupported slash bass note: {bass_name}")
            bass_pc = self.NOTE_MAP[bass_name]

        return {
            "root": root,
            "root_pc": root_pc,
            "canonical": canonical,
            "formula": formula,
            "chord_notes": chord_notes,
            "bass_pc": bass_pc,
        }

    def find_fretboard_notes(self, chord_notes):
        positions = []
        for string in range(6):
            for fret in range(self.max_fret+1):
                note = (self.tuning[string] + fret) % 12
                if note in chord_notes:
                    positions.append((string,fret))
        return positions

    def _normalize_inversion(self, inversion, formula):
        if inversion is None:
            return None
        max_inv = len(formula) - 1
        if isinstance(inversion, int):
            if 0 <= inversion <= max_inv:
                return inversion
            raise ValueError(f"Inversion out of range: {inversion}")

        lookup = {
            "root": 0,
            "root position": 0,
            "1st": 1,
            "first": 1,
            "2nd": 2,
            "second": 2,
            "3rd": 3,
            "third": 3,
        }
        key = str(inversion).strip().lower()
        if key not in lookup:
            raise ValueError(f"Unsupported inversion label: {inversion}")
        if lookup[key] > max_inv:
            raise ValueError(f"Inversion not available for this chord: {inversion}")
        return lookup[key]

    def _bass_note_pc(self, shape):
        for string, fret in enumerate(shape):
            if fret >= 0:
                return (self.tuning[string] + fret) % 12
        return None

    def _transpose_shape(self, template, shift):
        shifted = []
        for fret in template:
            if fret < 0:
                shifted.append(-1)
            else:
                shifted.append(fret + shift)
        return tuple(shifted)

    def _position_window(self, shape, window_size=4):
        fretted = [f for f in shape if f > 0]
        if not fretted:
            return (0, window_size)
        if max(fretted) <= window_size:
            return (0, window_size)
        start = min(fretted)
        return (start, start + window_size - 1)

    def _position_window_candidates(self, shape, window_size=4):
        start_fret, _ = self._position_window(shape, window_size=window_size)
        if start_fret > self.max_fret:
            return []

        max_start = max(0, self.max_fret - window_size + 1)
        base_start = min(start_fret, max_start)
        starts = list(range(base_start, max_start + 1))

        return [(s, s + window_size - 1) for s in starts]

    def _inject_bass(self, shape, target_bass_pc, chord_notes):
        bass_idx = next((i for i, fret in enumerate(shape) if fret >= 0), None)
        if bass_idx is None:
            return None

        start_fret, end_fret = self._position_window(shape)
        if start_fret > self.max_fret:
            return None
        end_fret = min(end_fret, self.max_fret)

        for string in range(bass_idx - 1, -1, -1):
            candidates = []
            open_pc = self.tuning[string] % 12
            if start_fret == 0 and open_pc == target_bass_pc and open_pc in chord_notes:
                candidates.append(0)

            low = max(1, start_fret)
            for fret in range(low, end_fret + 1):
                note_pc = (self.tuning[string] + fret) % 12
                if note_pc == target_bass_pc and note_pc in chord_notes:
                    candidates.append(fret)

            if candidates:
                injected = list(shape)
                injected[string] = min(candidates)
                return tuple(injected)

        return None

    def _closest_fret_for_tone(self, string, base_fret, start_fret, end_fret, chord_notes):
        candidates = []
        open_pc = self.tuning[string] % 12
        if start_fret == 0 and open_pc in chord_notes:
            candidates.append(0)

        low = max(1, start_fret)
        high = min(self.max_fret, end_fret)
        for fret in range(low, high + 1):
            pc = (self.tuning[string] + fret) % 12
            if pc in chord_notes:
                candidates.append(fret)

        if not candidates:
            return None

        return min(candidates, key=lambda f: (abs(f - base_fret), f))

    def _shape_note_set(self, shape):
        return {
            (self.tuning[string] + fret) % 12
            for string, fret in enumerate(shape)
            if fret >= 0
        }

    def _characteristic_pcs(self, root_pc, formula):
        must_include = {root_pc}

        # Keep quality tone (3rd/sus tone for most formulas).
        if len(formula) >= 2:
            must_include.add((root_pc + formula[1]) % 12)

        # Prefer explicit 7th when present.
        seventh = next((i for i in formula if i in (10, 11)), None)
        if seventh is not None:
            must_include.add((root_pc + seventh) % 12)

        # Ensure at least one characteristic extension/alteration for rich chords.
        extension_like = [
            i for i in formula
            if i not in (0, 3, 4, 5, 7, 10, 11)
        ]
        if extension_like:
            must_include.add((root_pc + extension_like[0]) % 12)

        return must_include

    def _closest_fret_for_specific_pc(self, string, base_fret, start_fret, end_fret, target_pc):
        candidates = []
        open_pc = self.tuning[string] % 12
        if start_fret == 0 and open_pc == target_pc:
            candidates.append(0)

        low = max(1, start_fret)
        high = min(self.max_fret, end_fret)
        for fret in range(low, high + 1):
            note_pc = (self.tuning[string] + fret) % 12
            if note_pc == target_pc:
                candidates.append(fret)

        if not candidates:
            return None

        return min(candidates, key=lambda f: (abs(f - base_fret), f))

    def _enforce_characteristic_tones(self, shape, must_include, protected_strings=None):
        protected_strings = set(protected_strings or [])
        start_fret, end_fret = self._position_window(shape)
        adjusted = list(shape)
        notes = self._shape_note_set(shape)

        for target_pc in must_include:
            if target_pc in notes:
                continue

            replaced = False
            for pass_idx in range(2):
                for string, current_fret in enumerate(adjusted):
                    if current_fret < 0:
                        continue
                    if pass_idx == 0 and string in protected_strings:
                        continue

                    new_fret = self._closest_fret_for_specific_pc(
                        string,
                        base_fret=current_fret,
                        start_fret=start_fret,
                        end_fret=end_fret,
                        target_pc=target_pc,
                    )
                    if new_fret is None:
                        continue

                    adjusted[string] = new_fret
                    notes = self._shape_note_set(tuple(adjusted))
                    replaced = True
                    break

                if replaced:
                    break

            if not replaced:
                return None

        return tuple(adjusted)

    def _fit_shape_to_chord(self, base_shape, chord_notes):
        windows = self._position_window_candidates(base_shape, window_size=4)
        if not windows:
            return None

        best_shape = None
        best_score = None
        for start_fret, end_fret in windows:
            end_fret = min(end_fret, self.max_fret)

            fitted = []
            for string, base_fret in enumerate(base_shape):
                if base_fret < 0:
                    fitted.append(-1)
                    continue

                best = self._closest_fret_for_tone(
                    string,
                    base_fret=base_fret,
                    start_fret=start_fret,
                    end_fret=end_fret,
                    chord_notes=chord_notes,
                )
                fitted.append(best if best is not None else -1)

            fitted = tuple(fitted)
            movement = sum(
                abs(new_fret - base_fret)
                for base_fret, new_fret in zip(base_shape, fitted)
                if base_fret >= 0 and new_fret >= 0
            )
            mute_penalty = sum(1 for f in fitted if f < 0)
            score = (movement, mute_penalty)

            if best_score is None or score < best_score:
                best_score = score
                best_shape = fitted

        return best_shape

    def _enumerate_non_major_variants(self, shape, chord_notes, must_include, root_pc, target_bass_pc):
        windows = self._position_window_candidates(shape, window_size=4)
        if not windows:
            return []

        variants = []
        seen = set()
        for start_fret, end_fret in windows:
            end_fret = min(end_fret, self.max_fret)

            per_string_options = []
            window_valid = True
            for string, template_fret in enumerate(shape):
                if template_fret < 0:
                    per_string_options.append([-1])
                    continue

                options = []
                # For rich chords, muting a non-essential string can create practical voicings.
                options.append(-1)
                open_pc = self.tuning[string] % 12
                if start_fret == 0 and open_pc in chord_notes:
                    options.append(0)

                low = max(1, start_fret)
                for fret in range(low, end_fret + 1):
                    pc = (self.tuning[string] + fret) % 12
                    if pc in chord_notes:
                        options.append(fret)

                options = sorted(set(options))
                if not options:
                    window_valid = False
                    break
                per_string_options.append(options)

            if not window_valid:
                continue

            for candidate in itertools.product(*per_string_options):
                candidate = tuple(candidate)
                if candidate in seen:
                    continue

                if any(fret > self.max_fret for fret in candidate if fret >= 0):
                    continue
                if sum(1 for fret in candidate if fret >= 0) < 3:
                    continue

                notes = self._shape_note_set(candidate)
                if root_pc not in notes:
                    continue
                if not must_include.issubset(notes):
                    continue

                if target_bass_pc is not None and self._bass_note_pc(candidate) != target_bass_pc:
                    continue

                seen.add(candidate)
                variants.append(candidate)

        return variants

    def _enumerate_major_mute_variants(self, shape, chord_notes, must_include, target_bass_pc=None, allow_bass_mute=False):
        variants = []
        seen = set()
        bass_idx = next((i for i, fret in enumerate(shape) if fret >= 0), None)
        if bass_idx is None:
            return variants

        mutable_indices = [
            i for i, fret in enumerate(shape)
            if fret >= 0 and (allow_bass_mute or i != bass_idx)
        ]

        for mask in range(1, 1 << len(mutable_indices)):
            candidate = list(shape)
            for bit, string in enumerate(mutable_indices):
                if (mask >> bit) & 1:
                    candidate[string] = -1

            candidate = tuple(candidate)
            if candidate in seen:
                continue
            if sum(1 for fret in candidate if fret >= 0) < 3:
                continue
            if target_bass_pc is not None and self._bass_note_pc(candidate) != target_bass_pc:
                continue

            notes = self._shape_note_set(candidate)
            if not must_include.issubset(notes):
                continue
            if any(((self.tuning[string] + fret) % 12) not in chord_notes for string, fret in enumerate(candidate) if fret >= 0):
                continue

            seen.add(candidate)
            variants.append(candidate)

        return variants

    def generate_chord_shapes(self, chord_name, max_results=5, inversion=None):
        info = self._parse_chord_info(chord_name)
        canonical = info["canonical"]
        root_pc = info["root_pc"]
        formula = info["formula"]

        inversion_idx = self._normalize_inversion(inversion, formula)
        target_bass_pc = info["bass_pc"]
        if inversion_idx is not None:
            target_bass_pc = (root_pc + formula[inversion_idx]) % 12

        # Keep max_results behavior consistent across chord types.
        # Pass max_results=None explicitly only when full enumeration is required.

        chord_notes = set(info["chord_notes"])
        must_include = self._characteristic_pcs(root_pc, formula)
        shapes = []
        seen_shapes = set()
        for frame_name, template_shape, template_root in self.FRAME_SKELETONS:
            template_root_pc = self.NOTE_MAP[template_root]
            shift = (root_pc - template_root_pc) % 12
            shifted_shape = self._transpose_shape(template_shape, shift)

            if any(fret > self.max_fret for fret in shifted_shape if fret >= 0):
                continue

            if canonical != "major":
                variants = self._enumerate_non_major_variants(
                    shifted_shape,
                    chord_notes=chord_notes,
                    must_include=must_include,
                    root_pc=root_pc,
                    target_bass_pc=target_bass_pc,
                )
                for variant in variants:
                    if variant in seen_shapes:
                        continue
                    seen_shapes.add(variant)
                    shapes.append((frame_name, variant))
                continue

            fitted_shape = self._fit_shape_to_chord(shifted_shape, chord_notes)
            if fitted_shape is None:
                continue
            if sum(1 for f in fitted_shape if f >= 0) < 3:
                continue

            protected_strings = set()
            if target_bass_pc is None:
                bass_idx = next((i for i, fret in enumerate(fitted_shape) if fret >= 0), None)
                if bass_idx is not None:
                    bass_pc = (self.tuning[bass_idx] + fitted_shape[bass_idx]) % 12
                    if bass_pc == root_pc:
                        protected_strings.add(bass_idx)

            fitted_shape = self._enforce_characteristic_tones(
                fitted_shape,
                must_include,
                protected_strings=protected_strings,
            )
            if fitted_shape is None:
                continue
            present_notes = self._shape_note_set(fitted_shape)
            if root_pc not in present_notes:
                continue

            candidate_shapes = [fitted_shape]
            if target_bass_pc is not None:
                bass_pc = self._bass_note_pc(fitted_shape)
                if bass_pc != target_bass_pc:
                    injected = self._inject_bass(fitted_shape, target_bass_pc, chord_notes)
                    candidate_shapes = [injected] if injected else []
            else:
                # Explore inversion-friendly bass notes for plain chords.
                current_bass = self._bass_note_pc(fitted_shape)
                for bass_pc in sorted(chord_notes):
                    if bass_pc == current_bass:
                        continue
                    injected = self._inject_bass(fitted_shape, bass_pc, chord_notes)
                    if injected is not None:
                        candidate_shapes.append(injected)

            expanded_shapes = []
            for base_shape in candidate_shapes:
                if base_shape is None:
                    continue
                expanded_shapes.append(base_shape)
                expanded_shapes.extend(
                    self._enumerate_major_mute_variants(
                        base_shape,
                        chord_notes=chord_notes,
                        must_include=must_include,
                        target_bass_pc=target_bass_pc,
                        allow_bass_mute=(target_bass_pc is None),
                    )
                )
            candidate_shapes = expanded_shapes

            for candidate in candidate_shapes:
                if candidate is None:
                    continue
                if candidate in seen_shapes:
                    continue
                seen_shapes.add(candidate)
                shapes.append((frame_name, candidate))

        def shape_score(item):
            _, shape = item
            fretted = [f for f in shape if f > 0]
            min_fretted = min(fretted) if fretted else 0
            mute_count = sum(1 for f in shape if f < 0)
            return (min_fretted, mute_count)

        shapes.sort(key=shape_score)
        shapes = self._prune_muted_subset_shapes(
            shapes,
            preserve_required_mutes=(target_bass_pc is None),
        )
        if max_results is None:
            return shapes
        return shapes[:max_results]

    def _inversion_rank(self, bass_pc, root_pc, formula):
        if bass_pc == root_pc:
            return 0
        for idx, interval in enumerate(formula[1:], start=1):
            if (root_pc + interval) % 12 == bass_pc:
                return idx
        return len(formula) + 1

    def _shape_label(self, chord_name, shape, root_pc):
        bass_pc = self._bass_note_pc(shape)
        if bass_pc is None or bass_pc == root_pc:
            return chord_name

        chord_core = chord_name.split("/")[0]
        return f"{chord_core}/{self._pc_display_name(bass_pc)}"

    def _root_string_index(self, shape, root_pc):
        for string, fret in enumerate(shape):
            if fret < 0:
                continue
            if (self.tuning[string] + fret) % 12 == root_pc:
                return string
        return None

    def _root_string_key(self, root_string_idx):
        if root_string_idx is None:
            return "unknown"
        return str(6 - root_string_idx)

    def _root_string_title(self, root_string_idx):
        if root_string_idx is None:
            return "Root string unknown"
        return f"Root on string {6 - root_string_idx}"

    def _pc_display_name(self, pc):
        return self.DISPLAY_NOTE_NAMES[pc % 12]

    def _note_label_size(self, note_name, base_size, compact_size):
        if "/" in note_name:
            return compact_size
        return base_size

    def _inversion_name(self, inv_rank):
        if inv_rank <= 0:
            return "Root position"
        if inv_rank == 1:
            return "1st inversion"
        if inv_rank == 2:
            return "2nd inversion"
        if inv_rank == 3:
            return "3rd inversion"
        return f"{inv_rank}th inversion"

    def _shape_start_fret(self, shape, window_size=4):
        frets = [fret for fret in shape if fret > 0]
        if not frets:
            return 0
        if max(frets) <= window_size:
            return 0
        return min(frets)

    def _is_muted_subset_shape(self, fuller_shape, sparse_shape):
        muted_from_fuller = False
        for full_fret, sparse_fret in zip(fuller_shape, sparse_shape):
            if sparse_fret == full_fret:
                continue
            if sparse_fret < 0 and full_fret >= 0:
                muted_from_fuller = True
                continue
            return False
        return muted_from_fuller

    def _prune_muted_subset_shapes(self, shapes, preserve_required_mutes=True):
        required_mute_by_frame = {
            frame_name: {idx for idx, fret in enumerate(template_shape) if fret < 0}
            for frame_name, template_shape, _ in self.FRAME_SKELETONS
        }

        pruned = []
        for idx, item in enumerate(shapes):
            candidate_frame, candidate_shape = item
            dominated = False
            for jdx, other in enumerate(shapes):
                if idx == jdx:
                    continue
                other_frame, other_shape = other
                if candidate_frame != other_frame:
                    continue
                if self._is_muted_subset_shape(other_shape, candidate_shape):
                    # Keep shapes that change the bass note/inversion (e.g. G vs G/B).
                    candidate_bass = self._bass_note_pc(candidate_shape)
                    other_bass = self._bass_note_pc(other_shape)
                    if candidate_bass != other_bass:
                        continue

                    # Keep mute strings that are structurally required by the base frame.
                    muted_from_fuller = {
                        i
                        for i, (full_fret, cand_fret) in enumerate(zip(other_shape, candidate_shape))
                        if cand_fret < 0 and full_fret >= 0
                    }
                    if preserve_required_mutes:
                        required_mutes = required_mute_by_frame.get(candidate_frame, set())
                        if muted_from_fuller & required_mutes:
                            continue

                    dominated = True
                    break
            if not dominated:
                pruned.append(item)
        return pruned

    def _draw_chord_box(self, ax, shape, title, window_size=4):
        start_fret = self._shape_start_fret(shape, window_size=window_size)
        open_marker_y = -0.5

        ax.set_xlim(-0.7, 5.7)
        ax.set_ylim(window_size + 0.6, -1.15)
        ax.set_aspect("equal")
        ax.set_facecolor("none")

        for s in range(6):
            ax.plot([s, s], [0, window_size], color="black", linewidth=1.8)

        for f in range(window_size + 1):
            is_nut = f == 0 and start_fret == 0
            ax.plot(
                [0, 5],
                [f, f],
                color="black",
                linewidth=7 if is_nut else 1.8,
                solid_capstyle="butt",
            )

        for string, fret in enumerate(shape):
            if fret < 0:
                ax.text(string, open_marker_y, "X", ha="center", va="center", fontsize=12, color="black", fontweight="bold")
                continue

            if fret == 0 and start_fret == 0:
                note_pc = (self.tuning[string] + fret) % 12
                note_name = self._pc_display_name(note_pc)
                ax.scatter(
                    string,
                    open_marker_y,
                    s=280,
                    facecolors="none",
                    edgecolors="black",
                    linewidths=1.8,
                    zorder=6,
                    clip_on=False,
                )
                ax.text(
                    string,
                    open_marker_y,
                    note_name,
                    color="black",
                    fontsize=self._note_label_size(note_name, 8, 6),
                    fontweight="bold",
                    ha="center",
                    va="center",
                    zorder=7,
                    clip_on=False,
                )
                continue

            if start_fret == 0:
                y = fret - 0.5
            else:
                y = (fret - start_fret) + 0.5

            if 0.0 <= y <= window_size:
                ax.scatter(string, y, s=280, color="black", zorder=5, clip_on=False)
                note_pc = (self.tuning[string] + fret) % 12
                note_name = self._pc_display_name(note_pc)
                ax.text(
                    string,
                    y,
                    note_name,
                    color="white",
                    fontsize=self._note_label_size(note_name, 8, 6),
                    fontweight="bold",
                    ha="center",
                    va="center",
                    zorder=6,
                    clip_on=False,
                )

        if start_fret > 0:
            ax.text(-0.55, 0.5, f"{start_fret}fr", ha="right", va="center", fontsize=10, color="black")

        ax.set_title(title, fontsize=22, fontweight="bold", pad=10)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    def _save_figure(self, fig, output_path, dpi=360):
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        extension = os.path.splitext(output_path)[1].lower()
        if extension == ".pdf":
            fig.savefig(output_path, format="pdf", bbox_inches="tight", transparent=True)
        else:
            fig.savefig(output_path, dpi=dpi, bbox_inches="tight", transparent=True)

    def _midi_to_freq(self, midi_note):
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def _midi_to_note_name(self, midi_note):
        note_name = self._pc_display_name(midi_note % 12)
        octave = (midi_note // 12) - 1
        return f"{note_name}{octave}"

    def _shape_midi_notes(self, shape):
        notes = []
        for string, fret in enumerate(shape):
            if fret >= 0:
                notes.append(self.tuning[string] + fret)
        return notes

    def _pc_to_midi_near(self, pitch_class, target_midi=60):
        candidate = target_midi - ((target_midi - pitch_class) % 12)
        if candidate < target_midi:
            above = candidate + 12
            if abs(above - target_midi) < abs(candidate - target_midi):
                candidate = above
        while candidate < 48:
            candidate += 12
        while candidate > 84:
            candidate -= 12
        return candidate

    def _synthesize_tone(self, freq, duration=0.45, volume=0.3):
        frame_count = int(self.AUDIO_SAMPLE_RATE * duration)
        t = np.linspace(0, duration, frame_count, endpoint=False)
        wave = np.sin(2 * np.pi * freq * t)

        # Short attack/release envelope to avoid click noise.
        attack = max(1, int(0.01 * self.AUDIO_SAMPLE_RATE))
        release = max(1, int(0.03 * self.AUDIO_SAMPLE_RATE))
        envelope = np.ones(frame_count)
        envelope[:attack] = np.linspace(0.0, 1.0, attack)
        envelope[-release:] = np.linspace(1.0, 0.0, release)
        return wave * envelope * volume

    def _build_audio_wave(self, midi_notes, arpeggio=False):
        if not midi_notes:
            return None

        if arpeggio:
            pieces = []
            for note in midi_notes:
                pieces.append(self._synthesize_tone(self._midi_to_freq(note), duration=0.34, volume=0.32))
                pieces.append(np.zeros(int(self.AUDIO_SAMPLE_RATE * 0.03)))
            return np.concatenate(pieces)

        tone_waves = [self._synthesize_tone(self._midi_to_freq(note), duration=0.62, volume=0.27) for note in midi_notes]
        mix = np.sum(tone_waves, axis=0) / max(1, len(tone_waves))
        peak = np.max(np.abs(mix))
        if peak > 0:
            mix = 0.95 * (mix / peak)
        return mix

    def _play_wave_non_blocking(self, wave):
        if wave is None:
            return
        if sa is None:
            print("Audio playback requires package 'simpleaudio'. Install with: pip install simpleaudio")
            return

        audio_data = np.int16(np.clip(wave, -1.0, 1.0) * 32767)

        def _worker():
            play_obj = sa.play_buffer(audio_data, 1, 2, self.AUDIO_SAMPLE_RATE)
            play_obj.wait_done()

        threading.Thread(target=_worker, daemon=True).start()

    def _play_midi_notes(self, midi_notes, arpeggio=False):
        wave = self._build_audio_wave(midi_notes, arpeggio=arpeggio)
        self._play_wave_non_blocking(wave)

    def _show_audio_panel(self, chord_name, visible_shapes, info):
        if tk is None or ttk is None:
            print("Audio panel requires tkinter support in your Python build.")
            return

        panel = tk.Toplevel()
        panel.title(f"Audio Panel - {chord_name}")
        panel.geometry("1080x760")

        canvas = tk.Canvas(panel)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        container = ttk.Frame(canvas)

        container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        chord_pc_sequence = info["chord_notes"]
        chord_midi_notes = [self._pc_to_midi_near(pc, target_midi=60) for pc in chord_pc_sequence]

        header = ttk.Label(
            container,
            text="Click note buttons to hear tone. Each fingering has shape notes and chord tones.",
            font=("Helvetica", 11),
        )
        header.pack(anchor="w", padx=10, pady=(10, 6))

        for idx, item in enumerate(visible_shapes, start=1):
            _, root_string_idx, shape, label = item
            shape_midi = self._shape_midi_notes(shape)
            shape_unique_midi = sorted(set(shape_midi))
            fingering_text = " ".join("x" if fret < 0 else str(fret) for fret in shape)
            root_title = self._root_string_title(root_string_idx)

            card = ttk.LabelFrame(container, text=f"{idx}. {label} ({root_title})")
            card.pack(fill="x", padx=10, pady=8)

            ttk.Label(card, text=f"Fingering: {fingering_text}").pack(anchor="w", padx=8, pady=(6, 2))

            shape_names = [self._midi_to_note_name(note) for note in shape_unique_midi]
            ttk.Label(card, text=f"Shape Notes: {' '.join(shape_names)}").pack(anchor="w", padx=8, pady=(2, 4))

            chord_names = [self._pc_display_name(pc) for pc in chord_pc_sequence]
            ttk.Label(card, text=f"Chord Tones: {' '.join(chord_names)}").pack(anchor="w", padx=8, pady=(0, 6))

            row1 = ttk.Frame(card)
            row1.pack(anchor="w", padx=8, pady=(0, 6))
            ttk.Button(row1, text="Play Shape (Arp)", command=lambda notes=shape_midi: self._play_midi_notes(notes, arpeggio=True)).pack(side="left", padx=(0, 6))
            ttk.Button(row1, text="Play Shape (Chord)", command=lambda notes=shape_midi: self._play_midi_notes(notes, arpeggio=False)).pack(side="left", padx=(0, 10))
            for note in shape_unique_midi:
                ttk.Button(
                    row1,
                    text=self._midi_to_note_name(note),
                    command=lambda n=note: self._play_midi_notes([n], arpeggio=False),
                ).pack(side="left", padx=2)

            row2 = ttk.Frame(card)
            row2.pack(anchor="w", padx=8, pady=(0, 8))
            ttk.Button(row2, text="Play Chord Tones (Arp)", command=lambda notes=chord_midi_notes: self._play_midi_notes(notes, arpeggio=True)).pack(side="left", padx=(0, 6))
            ttk.Button(row2, text="Play Chord Tones (Chord)", command=lambda notes=chord_midi_notes: self._play_midi_notes(notes, arpeggio=False)).pack(side="left", padx=(0, 10))
            for pc in chord_pc_sequence:
                note = self._pc_to_midi_near(pc, target_midi=60)
                ttk.Button(
                    row2,
                    text=self._pc_display_name(pc),
                    command=lambda n=note: self._play_midi_notes([n], arpeggio=False),
                ).pack(side="left", padx=2)

        panel.focus_set()

    def _collect_visible_shapes(self, chord_name, max_shapes=None, inversion=None):
        info = self._parse_chord_info(chord_name)
        canonical = info["canonical"]
        root_pc = info["root_pc"]
        formula = info["formula"]

        shapes = self.generate_chord_shapes(chord_name, max_results=None, inversion=inversion)

        ordered = []
        for _, shape in shapes:
            bass_pc = self._bass_note_pc(shape)
            inv_rank = self._inversion_rank(bass_pc, root_pc, formula)
            label = self._shape_label(chord_name, shape, root_pc)
            root_string_idx = self._root_string_index(shape, root_pc)
            ordered.append((inv_rank, root_string_idx, shape, label))

        ordered.sort(key=lambda item: (item[0], item[1] if item[1] is not None else 99))

        dedup = []
        seen = set()
        for inv_rank, root_string_idx, shape, label in ordered:
            key = (shape, label)
            if key in seen:
                continue
            seen.add(key)
            dedup.append((inv_rank, root_string_idx, shape, label))

        visible_shapes = dedup
        return info, dedup, visible_shapes

    def build_all_shapes_figure(self, chord_name, max_shapes=10, inversion=None, dpi=220):
        dpi = max(80, min(int(dpi), self.MAX_UI_DPI))
        info, dedup, visible_shapes = self._collect_visible_shapes(
            chord_name,
            max_shapes=max_shapes,
            inversion=inversion,
        )
        if not visible_shapes:
            return None, info, dedup, visible_shapes

        fig = self._build_figure_for_shapes(visible_shapes, dpi=dpi)
        return fig, info, dedup, visible_shapes

    def _build_figure_for_shapes(self, visible_shapes, dpi=220):
        if not visible_shapes:
            return None

        cols = min(4, len(visible_shapes))
        rows = (len(visible_shapes) + cols - 1) // cols
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 3.0, rows * 4.2), dpi=dpi, facecolor="none")
        fig.patch.set_alpha(0)

        if rows == 1 and cols == 1:
            axes_list = [axes]
        elif rows == 1 or cols == 1:
            axes_list = list(axes)
        else:
            axes_list = [ax for row_axes in axes for ax in row_axes]

        for idx, item in enumerate(visible_shapes):
            _, root_string_idx, shape, label = item
            root_title = self._root_string_title(root_string_idx)
            panel_title = label if len(visible_shapes) == 1 else f"{label} ({root_title})"
            self._draw_chord_box(axes_list[idx], shape, panel_title)

        for ax in axes_list[len(visible_shapes):]:
            ax.axis("off")

        plt.tight_layout(pad=1.2)
        return fig

    def plot_shape(self, shape, chord_name, title_suffix="", pdf_path=None, show=True, dpi=220, export_dpi=360):
        dpi = max(80, min(int(dpi), self.MAX_UI_DPI))
        export_dpi = max(100, min(int(export_dpi), self.MAX_EXPORT_DPI))
        if isinstance(shape, tuple) and len(shape) == 2:
            group_tag, fingering = shape
        else:
            group_tag, fingering = "", shape
        title = f"{chord_name} {title_suffix}".strip()
        if isinstance(group_tag, int):
            title = f"{title} ({self._root_string_title(group_tag)})".strip()
        elif isinstance(group_tag, str) and group_tag:
            title = f"{title} ({group_tag})".strip()
        fig, ax = plt.subplots(figsize=(2.8, 4.0), dpi=dpi, facecolor="none")
        fig.patch.set_alpha(0)
        self._draw_chord_box(ax, fingering, title)
        plt.tight_layout(pad=0.6)
        if pdf_path:
            self._save_figure(fig, pdf_path, dpi=export_dpi)
            print(f"Saved: {pdf_path}")
        if show:
            plt.show()
        else:
            plt.close(fig)

    def plot_all_shapes(self, chord_name, max_shapes=10, inversion=None, pdf_path=None, show=True, dpi=220, export_dpi=360, audio_panel=False):
        dpi = max(80, min(int(dpi), self.MAX_UI_DPI))
        export_dpi = max(100, min(int(export_dpi), self.MAX_EXPORT_DPI))
        fig, info, dedup, visible_shapes = self.build_all_shapes_figure(
            chord_name,
            max_shapes=max_shapes,
            inversion=inversion,
            dpi=dpi,
        )
        print(f"Total positions found: {len(dedup)}")
        if not visible_shapes:
            return
        if pdf_path:
            self._save_figure(fig, pdf_path, dpi=export_dpi)
            print(f"Saved: {pdf_path}")
        if show:
            plt.show()
        else:
            plt.close(fig)

        if audio_panel:
            self._show_audio_panel(chord_name, visible_shapes, info)

    def _shape_to_svg(self, shape, title, width=360, height=380, window_size=4):
        start_fret = self._shape_start_fret(shape, window_size=window_size)
        x0, y0 = 62, 62
        grid_w, grid_h = 250, 250
        dx = grid_w / 5
        dy = grid_h / window_size
        parts = [
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
            "<rect x='0' y='0' width='100%' height='100%' fill='white'/>",
        ]

        for s in range(6):
            x = x0 + s * dx
            parts.append(f"<line x1='{x:.2f}' y1='{y0}' x2='{x:.2f}' y2='{y0 + grid_h}' stroke='black' stroke-width='2' />")

        for f in range(window_size + 1):
            y = y0 + f * dy
            stroke_w = 8 if (f == 0 and start_fret == 0) else 2
            parts.append(f"<line x1='{x0}' y1='{y:.2f}' x2='{x0 + grid_w}' y2='{y:.2f}' stroke='black' stroke-width='{stroke_w}' />")

        open_marker_y = y0 - 18
        for string, fret in enumerate(shape):
            x = x0 + string * dx
            if fret < 0:
                parts.append(f"<text x='{x:.2f}' y='{open_marker_y}' text-anchor='middle' font-size='30' font-weight='700'>X</text>")
                continue

            if fret == 0 and start_fret == 0:
                pc = (self.tuning[string] + fret) % 12
                note_name = self._pc_display_name(pc)
                text_size = self._note_label_size(note_name, 14, 9)
                parts.append(f"<circle cx='{x:.2f}' cy='{open_marker_y - 4}' r='14' fill='white' stroke='black' stroke-width='2' />")
                parts.append(
                    f"<text x='{x:.2f}' y='{open_marker_y}' text-anchor='middle' font-size='{text_size}' font-weight='700'>{html.escape(note_name)}</text>"
                )
                continue

            if start_fret == 0:
                y = y0 + (fret - 0.5) * dy
            else:
                y = y0 + ((fret - start_fret) + 0.5) * dy
            if y0 <= y <= y0 + grid_h:
                pc = (self.tuning[string] + fret) % 12
                note_name = self._pc_display_name(pc)
                text_size = self._note_label_size(note_name, 12, 8)
                parts.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='14' fill='black' stroke='black' stroke-width='1' />")
                parts.append(
                    f"<text x='{x:.2f}' y='{y + 5:.2f}' fill='white' text-anchor='middle' font-size='{text_size}' font-weight='700'>{html.escape(note_name)}</text>"
                )

        if start_fret > 0:
            parts.append(f"<text x='{x0 - 12}' y='{y0 + dy/2:.2f}' text-anchor='end' font-size='24'>{start_fret}fr</text>")

        parts.append("</svg>")
        return "".join(parts)

    def get_shapes_grouped(self, chord_name, max_shapes=None, inversion=None, inversion_filter="all"):
        info, dedup, visible_shapes = self._collect_visible_shapes(
            chord_name,
            max_shapes=max_shapes,
            inversion=inversion,
        )

        inversion_counts = {
            "root": 0,
            "1st": 0,
            "2nd": 0,
            "3rd": 0,
        }
        for inv_rank, _, _, _ in dedup:
            if inv_rank == 0:
                inversion_counts["root"] += 1
            elif inv_rank == 1:
                inversion_counts["1st"] += 1
            elif inv_rank == 2:
                inversion_counts["2nd"] += 1
            elif inv_rank == 3:
                inversion_counts["3rd"] += 1

        filter_map = {
            "all": None,
            "root": 0,
            "1st": 1,
            "2nd": 2,
            "3rd": 3,
        }
        key = str(inversion_filter or "all").strip().lower()
        selected_rank = filter_map.get(key, None)
        if selected_rank is not None:
            visible_shapes = [item for item in visible_shapes if item[0] == selected_rank]

        grouped = {"6": [], "5": [], "4": [], "3": [], "2": [], "1": [], "unknown": []}
        for inv_rank, root_string_idx, shape, label in visible_shapes:
            root_key = self._root_string_key(root_string_idx)
            root_title = self._root_string_title(root_string_idx)
            panel_title = f"{label} ({root_title})"
            shape_midi = self._shape_midi_notes(shape)
            shape_unique = sorted(set(shape_midi))
            shape_names = [self._midi_to_note_name(note) for note in shape_unique]
            shape_freqs = [self._midi_to_freq(note) for note in shape_unique]
            group_idx = len(grouped.get(root_key, [])) + 1
            item = {
                "label": label,
                "title": panel_title,
                "anchor": f"shape-s{root_key}-{group_idx}",
                "shape": list(shape),
                "fingering": " ".join("x" if f < 0 else str(f) for f in shape),
                "root_string": None if root_string_idx is None else (6 - root_string_idx),
                "root_group": root_title,
                "inversion": self._inversion_name(inv_rank),
                "is_inversion": inv_rank > 0,
                "shape_note_names": shape_names,
                "shape_note_freqs": shape_freqs,
                "svg": self._shape_to_svg(shape, panel_title),
            }
            grouped.setdefault(root_key, []).append(item)

        group_order = ["6", "5", "4", "3", "2", "1", "unknown"]
        group_labels = {
            "6": "Root on string 6",
            "5": "Root on string 5",
            "4": "Root on string 4",
            "3": "Root on string 3",
            "2": "Root on string 2",
            "1": "Root on string 1",
            "unknown": "Root string unknown",
        }

        return {
            "chord": chord_name,
            "total_found": len(dedup),
            "total_visible": len(visible_shapes),
            "inversion_filter": key,
            "inversion_counts": inversion_counts,
            "groups": grouped,
            "group_order": group_order,
            "group_labels": group_labels,
            "sample_base_freq": self._midi_to_freq(self.GUITAR_SAMPLE_MIDI),
        }


HTML_TEMPLATE = """
<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Guitar Chords Web App</title>
  <style>
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; background: #f6f7fb; color: #111; }
    .app { max-width: 1320px; margin: 0 auto; padding: 16px; }
    .toolbar { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; background: #fff; border: 1px solid #ddd; border-radius: 12px; padding: 12px; }
    input, button { font-size: 14px; padding: 8px 10px; border-radius: 8px; border: 1px solid #ccc; }
    button { cursor: pointer; background: #111; color: #fff; border-color: #111; }
    button:disabled { opacity: 0.4; cursor: not-allowed; }
    .meta { margin: 10px 0; font-size: 14px; }
    .jump { margin: 8px 0 12px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    .jump a { color: #0b57d0; text-decoration: none; border: 1px solid #c9d8ff; background: #eef3ff; border-radius: 999px; padding: 4px 10px; font-size: 13px; }
    .grid { display: grid; grid-template-columns: repeat(2, minmax(460px, 1fr)); gap: 14px; }
    .card { background: #fff; border: 1px solid #ddd; border-radius: 12px; padding: 12px; }
    .svg-wrap { border: 1px solid #efefef; border-radius: 8px; padding: 6px; background: #fff; overflow: auto; }
    .notes { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
    .notes button { background: #fff; color: #111; border: 1px solid #bbb; }
        .group-title { margin: 18px 0 8px; font-size: 20px; font-weight: 700; }
    @media (max-width: 1000px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class=\"app\">
    <div class=\"toolbar\">
                        <label>Chord <input id="chord" value="Cmaj" /></label>
                                <label>Inversion Filter
                                    <select id="inversion-filter">
                                        <option value="all" selected>All</option>
                                        <option value="root">Root position</option>
                                        <option value="1st">1st inversion</option>
                                        <option value="2nd">2nd inversion</option>
                                        <option value="3rd">3rd inversion</option>
                                    </select>
                                </label>
            <button id="search">Generate</button>
    </div>
    <div class=\"meta\" id=\"meta\"></div>
    <div class=\"jump\" id=\"jump\"></div>
    <div id=\"groups\"></div>
  </div>

  <script>
                let state = { chord: 'Cmaj', inversionFilter: 'all', page: 1, pageSize: 8, pageCount: 1 };
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        let sampleBuffer = null;
        let sampleBaseFreq = 110.0;

        async function ensureSampleLoaded() {
            if (sampleBuffer) return sampleBuffer;
            const res = await fetch('/audio/guitar.wav');
            if (!res.ok) throw new Error('guitar.wav not found. Put it in the project root.');
            const arr = await res.arrayBuffer();
            sampleBuffer = await audioCtx.decodeAudioData(arr);
            return sampleBuffer;
        }

        async function playFreq(freq, when = 0, velocity = 0.95) {
            const buf = await ensureSampleLoaded();
            const src = audioCtx.createBufferSource();
            src.buffer = buf;
            const loweredFreq = freq * 0.5;
            const rate = Math.max(0.25, Math.min(4.0, loweredFreq / sampleBaseFreq));
            src.playbackRate.value = rate;
            const gain = audioCtx.createGain();
            const t0 = audioCtx.currentTime + when;

            // Use the sample's natural duration after pitch shift.
            const naturalDuration = buf.duration / rate;
            const release = Math.min(0.03, naturalDuration * 0.2);
            const releaseStart = Math.max(t0 + 0.01, t0 + naturalDuration - release);

            gain.gain.setValueAtTime(0.0001, t0);
            gain.gain.exponentialRampToValueAtTime(velocity, t0 + 0.01);
            gain.gain.setValueAtTime(velocity, releaseStart);
            gain.gain.exponentialRampToValueAtTime(0.0001, t0 + naturalDuration);
            src.connect(gain).connect(audioCtx.destination);
            src.start(t0);
            src.stop(t0 + naturalDuration + 0.01);
    }

        async function playChord(freqs) {
            await ensureSampleLoaded();
            freqs.forEach(f => playFreq(f, 0, 0.9));
    }

        async function playArp(freqs) {
            await ensureSampleLoaded();
            freqs.forEach((f, i) => playFreq(f, i * 0.14, 0.9));
    }

    function noteButtons(names, freqs) {
      return names.map((name, idx) => `<button data-f='${freqs[idx]}'>${name}</button>`).join('');
    }

        async function fetchGroups() {
      const params = new URLSearchParams({
        chord: state.chord,
                inversion_filter: state.inversionFilter,
      });
            const res = await fetch(`/api/shapes-grouped?${params}`);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'request failed');
      }
      return res.json();
    }

        function render(data) {
            sampleBaseFreq = data.sample_base_freq || 110.0;
            const filterLabelMap = {
                all: 'All',
                root: 'Root',
                '1st': '1st',
                '2nd': '2nd',
                '3rd': '3rd',
            };
            const activeFilter = filterLabelMap[data.inversion_filter] || 'All';
            document.getElementById('meta').textContent = `Chord ${data.chord} | Filter ${activeFilter} | Matched ${data.total_visible} shapes`;
            const filterSelect = document.getElementById('inversion-filter');
            const counts = data.inversion_counts || {};
            const options = [
                { value: 'all', label: 'All' },
                { value: 'root', label: `Root position (${counts.root ?? 0})` },
                { value: '1st', label: `1st inversion (${counts['1st'] ?? 0})` },
                { value: '2nd', label: `2nd inversion (${counts['2nd'] ?? 0})` },
                { value: '3rd', label: `3rd inversion (${counts['3rd'] ?? 0})` },
            ];
            filterSelect.innerHTML = options.map(opt => `<option value='${opt.value}'>${opt.label}</option>`).join('');
            filterSelect.value = state.inversionFilter;

            const groups = document.getElementById('groups');
            const jump = document.getElementById('jump');
            const order = data.group_order || ['6', '5', '4', '3', '2', '1', 'unknown'];
            const labels = data.group_labels || {};

            const availableGroups = order.filter(key => (data.groups[key] || []).length > 0);
            const groupLinks = availableGroups.map(key => `<a href='#' data-group='${key}'>${labels[key] || key} (${(data.groups[key] || []).length})</a>`);

            state.pageCount = Math.max(1, availableGroups.length);
            state.page = Math.max(1, Math.min(state.page, state.pageCount));
            const activeGroup = availableGroups[state.page - 1] || null;
            const pageItems = activeGroup ? (data.groups[activeGroup] || []) : [];

            jump.innerHTML = groupLinks.join(' ');
            jump.querySelectorAll('a[data-group]').forEach(link => {
                link.onclick = (e) => {
                    e.preventDefault();
                    const target = link.getAttribute('data-group');
                    const idx = availableGroups.indexOf(target);
                    if (idx >= 0) {
                        state.page = idx + 1;
                        render(data);
                    }
                };
            });

            groups.innerHTML = activeGroup ? (() => {
                const cards = pageItems.map(item => `
                    <div class='card' id='${item.anchor}'>
                        <div>Fingering: ${item.fingering}</div>
                        <div>${item.root_group || ''}</div>
                        ${item.is_inversion ? `<div>Inversion: ${item.inversion}</div>` : ''}
                        <div class='svg-wrap'>${item.svg}</div>
                        <div class='notes'>
                            <span>Shape Notes:</span>
                            <button class='play-shape-arp'>Arpeggio</button>
                            <button class='play-shape-chord'>Chord</button>
                            ${noteButtons(item.shape_note_names, item.shape_note_freqs)}
                        </div>
                    </div>
                `).join('');
                return `<div class='group-title' id='grp-${activeGroup}'>${labels[activeGroup] || activeGroup} (${pageItems.length})</div><div class='grid'>${cards}</div>`;
            })() : '';

            const allCards = groups.querySelectorAll('.card');
            allCards.forEach((card, idx) => {
                const item = pageItems[idx];
                if (!item) return;
                card.querySelector('.play-shape-arp').onclick = () => playArp(item.shape_note_freqs);
                card.querySelector('.play-shape-chord').onclick = () => playChord(item.shape_note_freqs);
                card.querySelectorAll('button[data-f]').forEach(btn => {
                    btn.onclick = () => playFreq(parseFloat(btn.dataset.f), 0, 0.95);
                });
            });
        }

    async function load() {
      try {
                const data = await fetchGroups();
        render(data);
      } catch (e) {
        document.getElementById('meta').textContent = `Error: ${e.message}`;
      }
    }

        function runSearch(resetPage = true) {
      state.chord = document.getElementById('chord').value.trim() || 'C';
            state.inversionFilter = document.getElementById('inversion-filter').value;
            if (resetPage) {
            state.page = 1;
            }
      load();
        }

        document.getElementById('search').onclick = () => {
            runSearch(true);
    };

        document.getElementById('chord').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                runSearch(true);
            }
        });

        document.getElementById('inversion-filter').addEventListener('change', () => {
            runSearch(true);
        });

    load();
  </script>
</body>
</html>
"""


visualizer_web = GuitarChords()
app = Flask(__name__) if Flask is not None else None


if app is not None:
    @app.route("/")
    def index():
        return Response(HTML_TEMPLATE, mimetype="text/html")


    @app.route("/favicon.ico")
    def favicon():
        return Response(status=204)


    @app.route("/audio/guitar.wav")
    def audio_guitar():
        audio_path = os.path.join(os.path.dirname(__file__), "guitar.wav")
        if not os.path.exists(audio_path):
            return Response("guitar.wav not found", status=404)
        return send_file(audio_path, mimetype="audio/wav")


    @app.route("/api/shapes-grouped")
    def api_shapes_grouped():
        chord = request.args.get("chord", "Cmaj").strip()
        inversion = request.args.get("inversion", "").strip() or None
        inversion_filter = request.args.get("inversion_filter", "all").strip().lower() or "all"
        payload = visualizer_web.get_shapes_grouped(
            chord_name=chord,
            max_shapes=None,
            inversion=inversion,
            inversion_filter=inversion_filter,
        )
        return jsonify(payload)

if __name__ == "__main__":
    if app is None:
        raise RuntimeError("Flask is required. Install with: pip install flask")
    url = "http://127.0.0.1:5100"
    try:
        webbrowser.open(url)
    except Exception:
        pass
    app.run(host="127.0.0.1", port=5100, debug=False)