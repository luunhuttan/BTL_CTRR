from __future__ import annotations

from tkinter import simpledialog

from algorithms.algo_opt import (
	bellman_ford,
	bellman_ford_trace,
	bellman_ford_all_trace,
	dijkstra,
	dijkstra_trace,
	dijkstra_all_trace,
	ford_fulkerson,
	ford_fulkerson_trace,
	kruskal,
	kruskal_trace,
	prim,
	prim_trace,
)
from algorithms.algo_traversal import bfs, dfs, check_bipartite
from algorithms.algo_euler import (
	fleury_algorithm,
	hierholzer_algorithm,
	euler_classification,
	directed_euler_classification,
)


class AlgorithmRunner:
	"""Runs and animates algorithms step-by-step for a GraphApp instance."""

	def __init__(self, app):
		self.app = app
		# Animation player state (for Pause/Prev/Next)
		self._player = None

	def _can_schedule(self) -> bool:
		if getattr(self.app, "_closing", False):
			return False
		try:
			return bool(self.app.winfo_exists())
		except Exception:
			return False

	# --------- shared helpers ---------

	def cancel_animation(self):
		# Stop scheduled ticks
		if getattr(self.app, "_anim_after_id", None) is not None:
			try:
				self.app.after_cancel(self.app._anim_after_id)
			except Exception:
				pass
			self.app._anim_after_id = None
		# Clear interactive player
		self._player = None

	def _player_active(self) -> bool:
		return self._player is not None

	def toggle_pause(self) -> bool:
		"""Toggle pause/resume. Returns True when paused."""
		if not self._player_active():
			return True
		paused = bool(self._player.get("paused", False))
		if paused:
			self._player["paused"] = False
			# Resume auto-play
			self._player["auto"] = True
			self._schedule_player_tick()
			return False
		# Pause: only cancel scheduled tick, keep player state.
		self._player["paused"] = True
		if getattr(self.app, "_anim_after_id", None) is not None:
			try:
				self.app.after_cancel(self.app._anim_after_id)
			except Exception:
				pass
			self.app._anim_after_id = None
		return True

	def step_next(self):
		"""Manual step forward one frame (also pauses autoplay)."""
		if not self._player_active():
			return
		# Stop auto scheduling and pause
		try:
			if getattr(self.app, "_anim_after_id", None) is not None:
				self.app.after_cancel(self.app._anim_after_id)
				self.app._anim_after_id = None
		except Exception:
			self.app._anim_after_id = None
		self._player["paused"] = True
		self._player["auto"] = False

		idx = int(self._player.get("i", 0))
		n = int(self._player.get("n", 0))
		if n <= 0:
			return
		if idx >= n - 1:
			# Already at end
			return
		idx += 1
		self._player["i"] = idx
		self._render_player_frame(idx)

	def step_prev(self):
		"""Manual step backward one frame (also pauses autoplay)."""
		if not self._player_active():
			return
		try:
			if getattr(self.app, "_anim_after_id", None) is not None:
				self.app.after_cancel(self.app._anim_after_id)
				self.app._anim_after_id = None
		except Exception:
			self.app._anim_after_id = None
		self._player["paused"] = True
		self._player["auto"] = False

		idx = int(self._player.get("i", 0))
		if idx <= 0:
			return
		idx -= 1
		self._player["i"] = idx
		self._render_player_frame(idx)

	def _start_player(self, *, total_frames: int, render_frame, delay_ms: int = 500, on_complete=None, on_forward=None):
		"""Start an interactive animation player.

		Frames are indexed [0..total_frames-1]. render_frame(i) should fully render state for i.
		on_forward(i) (optional) is called only when first time reaching frame i.
		on_complete() (optional) is called when reaching the last frame for the first time.
		"""
		self.cancel_animation()
		try:
			n = max(1, int(total_frames))
		except Exception:
			n = 1
		self._player = {
			"n": n,
			"i": 0,
			"render": render_frame,
			"delay": int(delay_ms) if delay_ms is not None else 500,
			"paused": False,
			"auto": True,
			"max_seen": -1,
			"on_forward": on_forward,
			"on_complete": on_complete,
			"completed": False,
		}
		self._render_player_frame(0)
		self._schedule_player_tick()

	def _render_player_frame(self, idx: int):
		if not self._player_active():
			return
		n = int(self._player.get("n", 0))
		idx = max(0, min(int(idx), max(0, n - 1)))
		render = self._player.get("render")
		try:
			if callable(render):
				render(idx)
		except Exception:
			# Never crash UI due to a frame render
			pass

		# Call on_forward only once per newly reached max index
		try:
			max_seen = int(self._player.get("max_seen", -1))
		except Exception:
			max_seen = -1
		if idx > max_seen:
			self._player["max_seen"] = idx
			on_forward = self._player.get("on_forward")
			if callable(on_forward):
				try:
					on_forward(idx)
				except Exception:
					pass
			# Completion callback once
			if idx == n - 1 and not bool(self._player.get("completed", False)):
				self._player["completed"] = True
				on_complete = self._player.get("on_complete")
				if callable(on_complete):
					try:
						on_complete()
					except Exception:
						pass

	def _schedule_player_tick(self):
		if not self._player_active():
			return
		if bool(self._player.get("paused", False)):
			return
		if not bool(self._player.get("auto", True)):
			return
		if not self._can_schedule():
			self.app._anim_after_id = None
			return
		try:
			delay = int(self._player.get("delay", 500))
		except Exception:
			delay = 500
		self.app._anim_after_id = self.app.after(delay, self._player_tick)

	def _player_tick(self):
		if not self._player_active():
			self.app._anim_after_id = None
			return
		# advance one frame in auto mode
		idx = int(self._player.get("i", 0))
		n = int(self._player.get("n", 0))
		if idx >= n - 1:
			self.app._anim_after_id = None
			return
		idx += 1
		self._player["i"] = idx
		self._render_player_frame(idx)
		self._schedule_player_tick()

	def reset_visuals(self):
		for node in self.app.nodes:
			node.color = "#3B8ED0"
			node.text_color = "white"
		for edge in self.app.edges:
			edge.color = "gray70"

	def _highlight_reachable_nodes(self, dist: dict, start_id: int, color: str = "#2ECC71"):
		"""Tô màu tất cả đỉnh reachable (dist != ∞) từ start.

		Chỉ tô màu node; không đụng tới màu cạnh.
		"""
		reachable_ids = set()
		for nid, d in (dist or {}).items():
			try:
				if d != float('inf'):
					reachable_ids.add(int(nid))
			except Exception:
				continue
		for node in self.app.nodes:
			try:
				if int(node.id) in reachable_ids:
					node.color = color
			except Exception:
				continue

	def _highlight_shortest_path_tree_edges(
		self,
		prev: dict,
		dist: dict,
		start_id: int,
		directed: bool,
		color: str = "#2ECC71",
	):
		"""Tô màu các cạnh thuộc cây đường đi ngắn (theo prev).

		Với mỗi đỉnh v reachable (dist[v] != ∞) và v != start, tô cạnh prev[v]→v.
		"""
		if not prev or not dist:
			return

		def _find_edge(u, v):
			if directed:
				for e in self.app.edges:
					if int(e.start_node.id) == int(u) and int(e.end_node.id) == int(v):
						return e
				return None
			for e in self.app.edges:
				a = int(e.start_node.id)
				b = int(e.end_node.id)
				if (a == int(u) and b == int(v)) or (a == int(v) and b == int(u)):
					return e
			return None

		start = int(start_id)
		for v, d in dist.items():
			try:
				vv = int(v)
				if vv == start or d == float('inf'):
					continue
				u = prev.get(vv)
				if u is None:
					continue
				ed = _find_edge(int(u), vv)
				if ed is not None:
					ed.color = color
			except Exception:
				continue

	def _undirected_semi_euler_end(self, start_id: int | None):
		if start_id is None:
			return None
		deg = {}
		for e in self.app.edges:
			u = int(e.start_node.id)
			v = int(e.end_node.id)
			deg[u] = deg.get(u, 0) + 1
			deg[v] = deg.get(v, 0) + 1
			
		odd = [v for v, d in deg.items() if d % 2 == 1]
		if len(odd) != 2:
			return None
		return odd[1] if odd[0] == int(start_id) else odd[0]

	def _highlight_final_path(self, path, cost, algo_name: str = "Dijkstra", reset_first: bool = True):
		if reset_first:
			self.reset_visuals()

		path_nodes = set(path)
		for node in self.app.nodes:
			if int(node.id) in path_nodes:
				node.color = "yellow"

		path_pairs = list(zip(path, path[1:]))
		is_directed = bool(getattr(self.app, 'is_directed', False))
		if is_directed:
			path_pair_set = set(path_pairs)
			for edge in self.app.edges:
				u = int(edge.start_node.id)
				v = int(edge.end_node.id)
				if (u, v) in path_pair_set:
					edge.color = "yellow"
		else:
			path_pair_set = {frozenset((u, v)) for (u, v) in path_pairs}
			for edge in self.app.edges:
				u = int(edge.start_node.id)
				v = int(edge.end_node.id)
				if frozenset((u, v)) in path_pair_set:
					edge.color = "yellow"

		self.app.draw_graph()
		self.app.log(f"{algo_name}: Đường đi {path}, tổng chi phí={cost}", level='THÀNH CÔNG')

	def _ask_optional_end_id(self, title: str):
		"""Hỏi end_id dạng tùy chọn. Cancel/để trống => None."""
		raw = simpledialog.askstring(title, "End node id (Cancel/để trống để tính tất cả):")
		if raw is None:
			return None
		raw = str(raw).strip()
		if not raw:
			return None
		try:
			return int(raw)
		except Exception:
			return None

	def _reconstruct_path(self, prev: dict, start_id: int, end_id: int):
		path = []
		cur = int(end_id)
		start = int(start_id)
		while cur is not None:
			path.append(cur)
			if cur == start:
				break
			cur = prev.get(cur)
		if not path or path[-1] != start:
			return []
		path.reverse()
		return path

	def _log_all_distances(self, algo_name: str, start_id: int, dist: dict, directed: bool):
		mode = "có hướng" if directed else "vô hướng"
		pairs = []
		for nid in sorted(dist.keys()):
			d = dist[nid]
			ds = "∞" if d == float('inf') else str(d)
			pairs.append(f"{nid}:{ds}")
		joined = ", ".join(pairs)
		self.app.log(
			f"{algo_name}: Khoảng cách từ {start_id} tới tất cả đỉnh ({mode}): {joined}",
			level='THÀNH CÔNG',
		)

	def _log_all_paths(self, algo_name: str, start_id: int, dist: dict, prev: dict, directed: bool):
		"""Log đường đi ngắn nhất cụ thể từ start tới từng đỉnh."""
		mode = "có hướng" if directed else "vô hướng"
		self.app.log(f"{algo_name}: Đường đi ngắn nhất từ {start_id} tới từng đỉnh ({mode}):", level='THÔNG BÁO')
		for nid in sorted(dist.keys()):
			d = dist[nid]
			if int(nid) == int(start_id):
				self.app.log(f"- {start_id}→{nid}: [{start_id}] (chi phí=0)", level='THÔNG BÁO')
				continue
			if d == float('inf'):
				self.app.log(f"- {start_id}→{nid}: Không đi tới được (chi phí=∞)", level='THÔNG BÁO')
				continue
			path = self._reconstruct_path(prev, int(start_id), int(nid))
			if not path:
				# Fallback: shouldn't happen if dist is finite, but keep safe
				self.app.log(f"- {start_id}→{nid}: Không xác định đường đi (chi phí={d})", level='THÔNG BÁO')
				continue
			self.app.log(f"- {start_id}→{nid}: {path} (chi phí={d})", level='THÔNG BÁO')

	def run_bellman_ford(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Bellman-Ford: Không có đỉnh.", level='CẢNH BÁO')
			return

		start_id = simpledialog.askinteger("Bellman-Ford", "Start node id:")
		if start_id is None:
			return
		end_id = self._ask_optional_end_id("Bellman-Ford")

		directed = bool(getattr(self.app, 'is_directed', False))
		dist, prev, neg_cycle, trace = bellman_ford_all_trace(
			self.app.nodes,
			self.app.edges,
			start_id,
			directed=directed,
		)

		path_to_end = []
		cost_to_end = float('inf')
		if end_id is not None and end_id in dist and dist[end_id] != float('inf'):
			path_to_end = self._reconstruct_path(prev, int(start_id), int(end_id))
			cost_to_end = dist[end_id]

		def finish():
			if neg_cycle:
				self.reset_visuals()
				self.app.draw_graph()
				self.app.log("Bellman-Ford: Phát hiện chu trình âm (không xác định đường đi ngắn nhất).", level='LỖI')
				return
			# Color reachable nodes for start→all mode
			self.reset_visuals()
			self._highlight_reachable_nodes(dist, int(start_id))
			self._highlight_shortest_path_tree_edges(prev, dist, int(start_id), directed)
			self.app.draw_graph()
			self._log_all_distances("Bellman-Ford", int(start_id), dist, directed)
			self._log_all_paths("Bellman-Ford", int(start_id), dist, prev, directed)
			if end_id is not None:
				if path_to_end:
					# Overlay final path highlight without clearing reachable-node coloring
					self._highlight_final_path(path_to_end, cost_to_end, algo_name="Bellman-Ford", reset_first=False)
				else:
					self.app.log(f"Bellman-Ford: Không tìm thấy đường đi từ {start_id} tới {end_id}.", level='CẢNH BÁO')

		if trace:
			self.app.log(f"Bellman-Ford: Đang mô phỏng {len(trace)} bước...", level='THÔNG BÁO')
			self.animate_bellman_ford(trace, path_to_end, cost_to_end, neg_cycle, start_id, end_id, delay_ms=450, on_finish=finish)
			return

		finish()

	def animate_bellman_ford(self, trace, path, cost, neg_cycle, start_id, end_id, delay_ms=450, on_finish=None):
		# Backward/forward stepping requires deterministic re-render.
		self.cancel_animation()
		is_directed = bool(getattr(self.app, 'is_directed', False))
		node_by_id = {int(n.id): n for n in self.app.nodes}

		def _find_edge(u, v):
			if is_directed:
				for e in self.app.edges:
					if int(e.start_node.id) == int(u) and int(e.end_node.id) == int(v):
						return e
				return None
			for e in self.app.edges:
				a = int(e.start_node.id)
				b = int(e.end_node.id)
				if (a == int(u) and b == int(v)) or (a == int(v) and b == int(u)):
					return e
			return None

		def render_frame(frame_idx: int):
			self.reset_visuals()
			last_edge = None
			last_node = None
			limit = min(int(frame_idx), len(trace))
			for j in range(limit):
				# revert last highlights (like original per-step)
				if last_edge is not None:
					try:
						last_edge.color = "gray70"
					except Exception:
						pass
					last_edge = None
				if last_node is not None:
					try:
						last_node.color = "#3B8ED0"
					except Exception:
						pass
					last_node = None

				event = trace[j]
				etype = event[0]
				if etype == "relax":
					_t, _k, u, v, _old, _new = event
					edge = _find_edge(u, v)
					if edge is not None:
						edge.color = "yellow"
						last_edge = edge
					node = node_by_id.get(int(v))
					if node is not None:
						node.color = "yellow"
						last_node = node
				elif etype == "neg_cycle":
					_t, u, v = event
					edge = _find_edge(u, v)
					if edge is not None:
						edge.color = "yellow"
						last_edge = edge
					break

			self.app.draw_graph()

		def on_forward(frame_idx: int):
			if frame_idx <= 0:
				return
			j = frame_idx - 1
			if 0 <= j < len(trace):
				event = trace[j]
				etype = event[0]
				if etype == "pass_start":
					_t, k = event
					self.app.log(f"Bellman-Ford: Bắt đầu vòng relax {k}", level='THÔNG BÁO')
				elif etype == "pass_end":
					_t, k, updated = event
					if not updated:
						self.app.log(f"Bellman-Ford: Dừng sớm tại vòng {k} (không còn cập nhật)", level='THÔNG BÁO')
				elif etype == "relax":
					_t, k, u, v, old, new = event
					old_s = "∞" if old == float('inf') else str(old)
					self.app.log(f"Bellman-Ford: Vòng {k}, relax {u}→{v}: {old_s} → {new}", level='THÔNG BÁO')
				elif etype == "neg_cycle":
					self.app.log("Bellman-Ford: Phát hiện chu trình âm (không xác định đường đi ngắn nhất).", level='LỖI')
			if frame_idx == len(trace):
				# Call finish once for final log/output
				if on_finish is not None:
					try:
						on_finish()
					except Exception:
						pass
					return
				if neg_cycle:
					self.app.log("Bellman-Ford: Phát hiện chu trình âm (không xác định đường đi ngắn nhất).", level='LỖI')
					return
				if not path:
					self.app.log(f"Bellman-Ford: Không tìm thấy đường đi từ {start_id} tới {end_id}.", level='CẢNH BÁO')
					return
				self.app.log(f"Bellman-Ford: Hoàn thành.", level='THÀNH CÔNG')

		self._start_player(
			total_frames=len(trace) + 1,
			render_frame=render_frame,
			delay_ms=delay_ms,
			on_forward=on_forward,
		)

	def _mst_total_weight(self, mst_edges) -> int:
		"""Tính tổng trọng số của cây khung nhỏ nhất.

		mst_edges thường là list các đối tượng Edge (có thuộc tính .weight).
		"""
		total = 0
		for e in mst_edges or []:
			try:
				w = getattr(e, "weight", 0)
				total += int(w)
			except Exception:
				continue
		return total

	# --------- animations ---------

	def animate_dijkstra(self, trace, path, cost, delay_ms=500, on_finish=None):
		# Deterministic player rendering
		self.cancel_animation()
		node_by_id = {int(n.id): n for n in self.app.nodes}

		def render_frame(frame_idx: int):
			self.reset_visuals()
			settled_ids = set()
			last_relax_edge = None
			limit = min(int(frame_idx), len(trace))
			for j in range(limit):
				if last_relax_edge is not None:
					try:
						last_relax_edge.color = "gray70"
					except Exception:
						pass
					last_relax_edge = None
				event = trace[j]
				etype = event[0]
				if etype == "settle":
					_t, u, _du = event
					settled_ids.add(int(u))
					for sid in settled_ids:
						node = node_by_id.get(sid)
						if node is not None:
							node.color = "gray70"
					node = node_by_id.get(int(u))
					if node is not None:
						node.color = "yellow"
				elif etype == "relax":
					_t, u, v, _nd = event
					for edge in self.app.edges:
						if int(edge.start_node.id) == int(u) and int(edge.end_node.id) == int(v):
							edge.color = "yellow"
							last_relax_edge = edge
							break

			self.app.draw_graph()

		def on_forward(frame_idx: int):
			if frame_idx == len(trace):
				if on_finish is not None:
					try:
						on_finish()
					except Exception:
						pass
					return
				if path:
					self._highlight_final_path(path, cost, algo_name="Dijkstra")
					return
				self.app.log("Dijkstra: Không tìm thấy đường đi.", level='CẢNH BÁO')

		self._start_player(total_frames=len(trace) + 1, render_frame=render_frame, delay_ms=delay_ms, on_forward=on_forward)

	def animate_prim(self, trace, mst_edges, delay_ms=500):
		self.cancel_animation()

		def render_frame(frame_idx: int):
			self.reset_visuals()
			chosen = set()
			last_edge = None
			limit = min(int(frame_idx), len(trace))
			for j in range(limit):
				if last_edge is not None and id(last_edge) not in chosen:
					try:
						last_edge.color = "gray70"
					except Exception:
						pass
					last_edge = None
				event = trace[j]
				etype = event[0]
				if etype == "consider":
					_t, edge = event
					edge.color = "yellow"
					last_edge = edge
				elif etype == "accept":
					_t, edge = event
					chosen.add(id(edge))
					edge.color = "yellow"
					last_edge = None

			if frame_idx >= len(trace):
				self.reset_visuals()
				for e in mst_edges:
					e.color = "yellow"
				self.app.draw_graph()
				return

			self.app.draw_graph()

		def on_forward(frame_idx: int):
			j = frame_idx - 1
			if 0 <= j < len(trace):
				event = trace[j]
				etype = event[0]
				if etype == "start":
					_t, start_id = event
					self.app.log(f"Prim: Bắt đầu thành phần tại {start_id}", level='THÔNG BÁO')
			if frame_idx == len(trace):
				total = self._mst_total_weight(mst_edges)
				self.app.log(
					f"Prim: Hoàn thành. Cạnh={len(mst_edges)}, Tổng trọng số cây khung cực tiểu={total}",
					level='THÀNH CÔNG',
				)

		self._start_player(
			total_frames=len(trace) + 1,
			render_frame=render_frame,
			delay_ms=delay_ms,
			on_forward=on_forward,
		)

	def animate_kruskal(self, trace, mst_edges, delay_ms=500):
		self.cancel_animation()

		def render_frame(frame_idx: int):
			self.reset_visuals()
			chosen = set()
			last_edge = None
			limit = min(int(frame_idx), len(trace))
			for j in range(limit):
				if last_edge is not None and id(last_edge) not in chosen:
					try:
						last_edge.color = "gray70"
					except Exception:
						pass
					last_edge = None
				event = trace[j]
				etype = event[0]
				if etype == "start":
					continue
				if len(event) < 2:
					continue
				edge = event[1]
				if etype == "consider":
					edge.color = "yellow"
					last_edge = edge
				elif etype == "accept":
					chosen.add(id(edge))
					edge.color = "yellow"
					last_edge = None
				elif etype == "reject":
					edge.color = "yellow"
					last_edge = edge

			if frame_idx >= len(trace):
				self.reset_visuals()
				for e in mst_edges:
					e.color = "yellow"
				self.app.draw_graph()
				return

			self.app.draw_graph()

		def on_forward(frame_idx: int):
			j = frame_idx - 1
			if 0 <= j < len(trace):
				event = trace[j]
				etype = event[0]
				if etype == "start" and len(event) >= 2:
					start_id = event[1]
					self.app.log(f"Kruskal: Bắt đầu (đỉnh chọn) = {start_id}", level='THÔNG BÁO')
			if frame_idx == len(trace):
				total = self._mst_total_weight(mst_edges)
				self.app.log(
					f"Kruskal: Hoàn thành. Cạnh={len(mst_edges)}, Tổng trọng số={total}",
					level='THÀNH CÔNG',
				)

		self._start_player(
			total_frames=len(trace) + 1,
			render_frame=render_frame,
			delay_ms=delay_ms,
			on_forward=on_forward,
		)

	def animate_ford_fulkerson(self, trace, flow_network, max_flow, delay_ms=700):
		self.cancel_animation()

		def render_frame(frame_idx: int):
			self.reset_visuals()
			last_path_edges = []
			limit = min(int(frame_idx), len(trace))
			for j in range(limit):
				# clear last path
				for e in last_path_edges:
					try:
						e.color = "gray70"
					except Exception:
						pass
				last_path_edges = []
				event = trace[j]
				etype = event[0]
				if etype == "augment":
					_t, path_pairs, _bottleneck, _flow_after = event
					for (u, v) in path_pairs:
						for edge in self.app.edges:
							if int(edge.start_node.id) == int(u) and int(edge.end_node.id) == int(v):
								edge.color = "yellow"
								last_path_edges.append(edge)
								break

			if frame_idx >= len(trace):
				self.reset_visuals()
				for e in flow_network:
					if getattr(e, "flow", 0) > 0:
						e.color = "yellow"
				self.app.draw_graph()
				return

			self.app.draw_graph()

		def on_forward(frame_idx: int):
			j = frame_idx - 1
			if 0 <= j < len(trace):
				event = trace[j]
				etype = event[0]
				if etype == "augment":
					_t, _path_pairs, bottleneck, flow_after = event
					self.app.log(f"Ford-Fulkerson: Tăng thêm +{bottleneck} (luồng={flow_after})", level='THÔNG BÁO')
			if frame_idx == len(trace):
				self.app.log(f"Ford-Fulkerson: Hoàn thành. luồng cực đại={max_flow}", level='THÀNH CÔNG')

		self._start_player(
			total_frames=len(trace) + 1,
			render_frame=render_frame,
			delay_ms=delay_ms,
			on_forward=on_forward,
		)

	# --------- public handlers (called by GraphApp) ---------

	def run_dijkstra(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Dijkstra: Không có đỉnh.", level='CẢNH BÁO')
			return

		start_id = simpledialog.askinteger("Dijkstra", "Start node id:")
		if start_id is None:
			return
		end_id = self._ask_optional_end_id("Dijkstra")
		directed = bool(getattr(self.app, 'is_directed', False))

		# Dijkstra không hỗ trợ trọng số âm
		for e in self.app.edges:
			try:
				if int(getattr(e, 'weight', 0)) < 0:
					self.app.log("Dijkstra: Không hỗ trợ trọng số âm. Hãy dùng Bellman-Ford.", level='CẢNH BÁO')
					return
			except Exception:
				pass

		dist, prev, trace = dijkstra_all_trace(self.app.nodes, self.app.edges, start_id, directed=directed)
		path_to_end = []
		cost_to_end = float('inf')
		if end_id is not None and end_id in dist and dist[end_id] != float('inf'):
			path_to_end = self._reconstruct_path(prev, int(start_id), int(end_id))
			cost_to_end = dist[end_id]

		def finish():
			# Color reachable nodes for start→all mode
			self.reset_visuals()
			self._highlight_reachable_nodes(dist, int(start_id))
			self._highlight_shortest_path_tree_edges(prev, dist, int(start_id), directed)
			self.app.draw_graph()
			self._log_all_distances("Dijkstra", int(start_id), dist, directed)
			self._log_all_paths("Dijkstra", int(start_id), dist, prev, directed)
			if end_id is not None:
				if path_to_end:
					# Overlay final path highlight without clearing reachable-node coloring
					self._highlight_final_path(path_to_end, cost_to_end, algo_name="Dijkstra", reset_first=False)
				else:
					self.app.log(f"Dijkstra: Không tìm thấy đường đi từ {start_id} tới {end_id}.", level='CẢNH BÁO')

		if trace:
			self.app.log(f"Dijkstra: Đang mô phỏng {len(trace)} bước...", level='THÔNG BÁO')
			self.animate_dijkstra(trace, path_to_end, cost_to_end, delay_ms=500, on_finish=finish)
			return

		finish()

	def run_prim(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Prim: Không có đỉnh.", level='CẢNH BÁO')
			return

		start_id = simpledialog.askinteger("Prim", "Start node id:")
		if start_id is None:
			return
		node_ids = {int(n.id) for n in self.app.nodes}
		if int(start_id) not in node_ids:
			self.app.log(f"Prim: Đỉnh bắt đầu {start_id} không tồn tại.", level='CẢNH BÁO')
			return

		mst, trace = prim_trace(self.app.nodes, self.app.edges, start_id)
		if trace:
			self.app.log(f"Prim: Đang mô phỏng {len(trace)} bước...", level='THÔNG BÁO')
			self.animate_prim(trace, mst, delay_ms=500)
			return

		mst2 = prim(self.app.nodes, self.app.edges, start_id)
		self.reset_visuals()
		for e in mst2:
			e.color = "yellow"
		self.app.draw_graph()
		total = self._mst_total_weight(mst2)
		self.app.log(
			f"Prim: Hoàn thành. Cạnh={len(mst2)}, Tổng trọng số của cây khung cực tiểu ={total}",
			level='THÀNH CÔNG',
		)

	def run_kruskal(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Kruskal: Không có đỉnh.", level='CẢNH BÁO')
			return

		start_id = simpledialog.askinteger("Kruskal", "Start node id:")
		if start_id is None:
			return
		node_ids = {int(n.id) for n in self.app.nodes}
		if int(start_id) not in node_ids:
			self.app.log(f"Kruskal: Đỉnh bắt đầu {start_id} không tồn tại.", level='CẢNH BÁO')
			return

		mst, trace = kruskal_trace(self.app.nodes, self.app.edges, start_id)
		if trace:
			self.app.log(f"Kruskal: Đang mô phỏng {len(trace)} bước...", level='THÔNG BÁO')
			self.animate_kruskal(trace, mst, delay_ms=400)
			return

		mst2 = kruskal(self.app.nodes, self.app.edges, start_id)
		self.reset_visuals()
		for e in mst2:
			e.color = "yellow"
		self.app.draw_graph()
		total = self._mst_total_weight(mst2)
		self.app.log(
			f"Kruskal: Hoàn thành. Cạnh={len(mst2)}, Tổng trọng số cây khung cực tiểu ={total}",
			level='THÀNH CÔNG',
		)

	def run_ford_fulkerson(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Ford-Fulkerson: Không có đỉnh.", level='CẢNH BÁO')
			return

		source_id = simpledialog.askinteger("Ford-Fulkerson", "Source node id:")
		if source_id is None:
			return
		sink_id = simpledialog.askinteger("Ford-Fulkerson", "Sink node id:")
		if sink_id is None:
			return

		max_flow, flow_network, trace = ford_fulkerson_trace(
			self.app.nodes, self.app.edges, source_id, sink_id
		)
		if trace:
			self.app.log(f"Ford-Fulkerson: Đang mô phỏng {len(trace)} lần tăng luồng...", level='THÔNG BÁO')
			self.animate_ford_fulkerson(trace, flow_network, max_flow, delay_ms=800)
			return

		max_flow2, flow_network2 = ford_fulkerson(self.app.nodes, self.app.edges, source_id, sink_id)
		self.reset_visuals()
		for edge in flow_network2:
			if getattr(edge, "flow", 0) > 0:
				edge.color = "yellow"
		self.app.draw_graph()
		self.app.log(f"Ford-Fulkerson: Hoàn thành. luồng cực đại={max_flow2}", level='THÀNH CÔNG')

	def run_bfs(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("BFS: Không có đỉnh.", level='CẢNH BÁO')
			return

		start_id = simpledialog.askinteger("BFS", "Start node id:")
		if start_id is None:
			return

		path = bfs(self.app.nodes, self.app.edges, start_id)
		if not path:
			self.app.log(f"BFS: Không tìm thấy đường đi từ {start_id}.", level='CẢNH BÁO')
			return

		# In ra thứ tự duyệt
		try:
			order_str = " → ".join(str(int(x)) for x in path)
		except Exception:
			order_str = str(path)
		self.app.log(f"BFS: Thứ tự duyệt: {order_str}", level='THÔNG BÁO')

		unvisited = sorted({int(n.id) for n in self.app.nodes} - {int(x) for x in path})
		if unvisited:
			mode = "có hướng" if bool(getattr(self.app, 'is_directed', False)) else "vô hướng"
			self.app.log(
				f"BFS: Không đi tới được các đỉnh {unvisited} từ {start_id} (đồ thị {mode}).",
				level='THÔNG BÁO',
			)

		self.app.log(f"BFS: Đã thăm {len(path)} đỉnh. Đang mô phỏng...", level='THÔNG BÁO')
		self.animate_traversal(path, "BFS")

	def run_dfs(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("DFS: Không có đỉnh.", level='CẢNH BÁO')
			return

		start_id = simpledialog.askinteger("DFS", "Start node id:")
		if start_id is None:
			return

		path = dfs(self.app.nodes, self.app.edges, start_id)
		if not path:
			self.app.log(f"DFS: Không tìm thấy đường đi từ {start_id}.", level='CẢNH BÁO')
			return

		# In ra thứ tự duyệt
		try:
			order_str = " → ".join(str(int(x)) for x in path)
		except Exception:
			order_str = str(path)
		self.app.log(f"DFS: Thứ tự duyệt: {order_str}", level='THÔNG BÁO')

		unvisited = sorted({int(n.id) for n in self.app.nodes} - {int(x) for x in path})
		if unvisited:
			mode = "có hướng" if bool(getattr(self.app, 'is_directed', False)) else "vô hướng"
			self.app.log(
				f"DFS: Không đi tới được các đỉnh {unvisited} từ {start_id} (đồ thị {mode}).",
				level='THÔNG BÁO',
			)

		self.app.log(f"DFS: Đã thăm {len(path)} đỉnh. Đang mô phỏng...", level='THÔNG BÁO')
		self.animate_traversal(path, "DFS")

	def animate_traversal(self, path_ids, algo_name, delay_ms=500):
		self.cancel_animation()
		node_map = {n.id: n for n in self.app.nodes}

		def render_frame(frame_idx: int):
			self.reset_visuals()
			k = min(int(frame_idx), len(path_ids))
			for t in range(k):
				nid = path_ids[t]
				node = node_map.get(nid)
				if node is not None:
					node.color = "yellow"
			self.app.draw_graph()

		def on_forward(frame_idx: int):
			if frame_idx == len(path_ids):
				self.app.log(f"{algo_name}: Hoàn thành.", level='THÀNH CÔNG')

		self._start_player(
			total_frames=len(path_ids) + 1,
			render_frame=render_frame,
			delay_ms=delay_ms,
			on_forward=on_forward,
		)

	def run_check_bipartite(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Kiểm tra hai phía: Không có đỉnh.", level='CẢNH BÁO')
			return

		is_bipartite, color_map = check_bipartite(self.app.nodes, self.app.edges)
		
		self.reset_visuals()
		if is_bipartite:
			self.app.log("Đồ thị là đồ thị hai phía. Đang tô màu...", level='THÔNG BÁO')
			for node in self.app.nodes:
				c = color_map.get(node.id)
				if c == 0:
					node.color = "#E74C3C" # Red
				elif c == 1:
					node.color = "#2ECC71" # Green
		else:
			self.app.log("Đồ thị KHÔNG phải đồ thị hai phía.", level='CẢNH BÁO')
			# Highlight conflict if possible, but color_map might be partial
			# Just show what we have
			for node in self.app.nodes:
				if node.id in color_map:
					c = color_map[node.id]
					if c == 0:
						node.color = "#E74C3C"
					elif c == 1:
						node.color = "#2ECC71"
		
		self.app.draw_graph()

	def animate_euler(self, path_ids, algo_name, delay_ms=800):
		self.cancel_animation()
		node_map = {n.id: n for n in self.app.nodes}
		is_directed = bool(getattr(self.app, 'is_directed', False))

		def render_frame(frame_idx: int):
			self.reset_visuals()
			# Rebuild edge map each render so stepping backward is deterministic.
			edge_map = {}
			for e in self.app.edges:
				u, v = int(e.start_node.id), int(e.end_node.id)
				if is_directed:
					edge_map.setdefault((u, v), []).append(e)
				else:
					key = frozenset((u, v))
					edge_map.setdefault(key, []).append(e)

			k = min(int(frame_idx), len(path_ids))
			if k > 0 and path_ids:
				n0 = node_map.get(path_ids[0])
				if n0 is not None:
					n0.color = "yellow"

			for i in range(1, k):
				u_id = path_ids[i - 1]
				v_id = path_ids[i]
				node = node_map.get(v_id)
				if node is not None:
					node.color = "yellow"
				key = (u_id, v_id) if is_directed else frozenset((u_id, v_id))
				lst = edge_map.get(key)
				if lst:
					ed = lst.pop(0)
					ed.color = "red"

			self.app.draw_graph()

		def on_forward(frame_idx: int):
			if frame_idx == len(path_ids):
				self.app.log(f"{algo_name}: Hoàn thành.", level='THÀNH CÔNG')

		self._start_player(
			total_frames=len(path_ids) + 1,
			render_frame=render_frame,
			delay_ms=delay_ms,
			on_forward=on_forward,
		)

	def run_fleury(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Fleury: Không có đỉnh.", level='CẢNH BÁO')
			return
		
		is_directed = bool(getattr(self.app, 'is_directed', False))
		if is_directed:
			kind, start_id, end_id = directed_euler_classification(self.app.nodes, self.app.edges)
			if kind == "none":
				self.app.log("Fleury: Đồ thị không có chu trình/đường đi Euler có hướng.", level='CẢNH BÁO')
				return
			if kind == "euler":
				self.app.log(f"Fleury: Đồ thị có chu trình Euler có hướng (bắt đầu tại {start_id}).", level='THÔNG BÁO')
			else:
				self.app.log(
					f"Fleury: Đồ thị có đường đi Euler có hướng từ {start_id} đến {end_id}.",
					level='THÔNG BÁO',
				)
		else:
			kind, start_id = euler_classification(self.app.nodes, self.app.edges)
			if kind == "none":
				self.app.log("Fleury: Đồ thị không có chu trình/đường đi Euler.", level='CẢNH BÁO')
				return
			if kind == "euler":
				self.app.log(f"Fleury: Đồ thị có chu trình Euler (bắt đầu tại {start_id}).", level='THÔNG BÁO')
			else:
				end_id = self._undirected_semi_euler_end(start_id)
				if end_id is not None:
					self.app.log(
						f"Fleury: Đồ thị có đường đi Euler (nửa Euler) từ {start_id} đến {end_id}.",
						level='THÔNG BÁO',
					)
				else:
					self.app.log(
						f"Fleury: Đồ thị có đường đi Euler (nửa Euler), bắt đầu tại {start_id}.",
						level='THÔNG BÁO',
					)
		
		path = fleury_algorithm(self.app.nodes, self.app.edges, directed=is_directed)
		if not path:
			self.app.log("Fleury: Không dựng được đường đi/chu trình Euler.", level='CẢNH BÁO')
			return
			
		self.app.log(f"Fleury: Tìm thấy đường đi/chu trình với {len(path)} đỉnh. Đang mô phỏng...", level='THÔNG BÁO')
		self.animate_euler(path, "Fleury")

	def run_hierholzer(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Hierholzer: Không có đỉnh.", level='CẢNH BÁO')
			return

		is_directed = bool(getattr(self.app, 'is_directed', False))
		if is_directed:
			kind, start_id, end_id = directed_euler_classification(self.app.nodes, self.app.edges)
			if kind == "none":
				self.app.log("Hierholzer: Đồ thị không có chu trình/đường đi Euler có hướng.", level='CẢNH BÁO')
				return
			if kind == "euler":
				self.app.log(f"Hierholzer: Đồ thị có chu trình Euler có hướng (bắt đầu tại {start_id}).", level='THÔNG BÁO')
			else:
				self.app.log(
					f"Hierholzer: Đồ thị có đường đi Euler có hướng từ {start_id} đến {end_id}.",
					level='THÔNG BÁO',
				)
		else:
			kind, start_id = euler_classification(self.app.nodes, self.app.edges)
			if kind == "none":
				self.app.log("Hierholzer: Đồ thị không có chu trình/đường đi Euler.", level='CẢNH BÁO')
				return
			if kind == "euler":
				self.app.log(f"Hierholzer: Đồ thị có chu trình Euler (bắt đầu tại {start_id}).", level='THÔNG BÁO')
			else:
				end_id = self._undirected_semi_euler_end(start_id)
				if end_id is not None:
					self.app.log(
						f"Hierholzer: Đồ thị có đường đi Euler (nửa Euler) từ {start_id} đến {end_id}.",
						level='THÔNG BÁO',
					)
				else:
					self.app.log(
						f"Hierholzer: Đồ thị có đường đi Euler (nửa Euler), bắt đầu tại {start_id}.",
						level='THÔNG BÁO',
					)
		
		path = hierholzer_algorithm(self.app.nodes, self.app.edges, directed=is_directed)
		if not path:
			self.app.log("Hierholzer: Không dựng được đường đi/chu trình Euler.", level='CẢNH BÁO')
			return
			
		self.app.log(f"Hierholzer: Tìm thấy đường đi/chu trình với {len(path)} đỉnh. Đang mô phỏng...", level='THÔNG BÁO')
		self.animate_euler(path, "Hierholzer")
