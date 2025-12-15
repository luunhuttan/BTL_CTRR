from __future__ import annotations

from tkinter import simpledialog

from algorithms.algo_opt import (
	bellman_ford,
	dijkstra,
	dijkstra_trace,
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

	def _can_schedule(self) -> bool:
		if getattr(self.app, "_closing", False):
			return False
		try:
			return bool(self.app.winfo_exists())
		except Exception:
			return False

	# --------- shared helpers ---------

	def cancel_animation(self):
		if getattr(self.app, "_anim_after_id", None) is not None:
			try:
				self.app.after_cancel(self.app._anim_after_id)
			except Exception:
				pass
			self.app._anim_after_id = None

	def reset_visuals(self):
		for node in self.app.nodes:
			node.color = "#3B8ED0"
			node.text_color = "white"
		for edge in self.app.edges:
			edge.color = "gray70"

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

	def _highlight_final_path(self, path, cost, algo_name: str = "Dijkstra"):
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

	def run_bellman_ford(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Bellman-Ford: Không có đỉnh.", level='CẢNH BÁO')
			return

		start_id = simpledialog.askinteger("Bellman-Ford", "Start node id:")
		if start_id is None:
			return
		end_id = simpledialog.askinteger("Bellman-Ford", "End node id:")
		if end_id is None:
			return

		directed = bool(getattr(self.app, 'is_directed', False))
		path, cost, neg_cycle = bellman_ford(self.app.nodes, self.app.edges, start_id, end_id, directed=directed)
		if neg_cycle:
			self.reset_visuals()
			self.app.draw_graph()
			self.app.log("Bellman-Ford: Phát hiện chu trình âm (không xác định đường đi ngắn nhất).", level='LỖI')
			return
		if not path:
			self.reset_visuals()
			self.app.draw_graph()
			self.app.log(f"Bellman-Ford: Không tìm thấy đường đi từ {start_id} tới {end_id}.", level='CẢNH BÁO')
			return
		self._highlight_final_path(path, cost, algo_name="Bellman-Ford")

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

	def animate_dijkstra(self, trace, path, cost, delay_ms=500):
		self.cancel_animation()
		self.reset_visuals()
		self.app.draw_graph()

		node_by_id = {int(n.id): n for n in self.app.nodes}
		settled_ids = set()
		last_relax_edge = None
		i = 0

		def step():
			nonlocal i, last_relax_edge

			if not self._can_schedule():
				self.app._anim_after_id = None
				return

			if i >= len(trace):
				self.app._anim_after_id = None
				if path:
					self._highlight_final_path(path, cost)
				else:
					self.reset_visuals()
					self.app.draw_graph()
					self.app.log("Dijkstra: Không tìm thấy đường đi.", level='CẢNH BÁO')
				return

			if last_relax_edge is not None:
				last_relax_edge.color = "gray70"
				last_relax_edge = None

			event = trace[i]
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
			i += 1
			if not self._can_schedule():
				self.app._anim_after_id = None
				return
			self.app._anim_after_id = self.app.after(delay_ms, step)

		step()

	def animate_prim(self, trace, mst_edges, delay_ms=500):
		self.cancel_animation()
		self.reset_visuals()
		self.app.draw_graph()

		chosen = set()
		last_edge = None
		i = 0

		def step():
			nonlocal i, last_edge

			if not self._can_schedule():
				self.app._anim_after_id = None
				return

			if i >= len(trace):
				self.app._anim_after_id = None
				self.reset_visuals()
				for e in mst_edges:
					e.color = "yellow"
				self.app.draw_graph()
				total = self._mst_total_weight(mst_edges)
				self.app.log(
					f"Prim: Hoàn thành. Cạnh={len(mst_edges)}, Tổng trọng số cây khung cực tiểu={total}",
					level='THÀNH CÔNG',
				)
				return

			if last_edge is not None and id(last_edge) not in chosen:
				last_edge.color = "gray70"
				last_edge = None

			event = trace[i]
			etype = event[0]
			if etype == "start":
				_t, start_id = event
				self.app.log(f"Prim: Bắt đầu thành phần tại {start_id}", level='THÔNG BÁO')
			elif etype == "consider":
				_t, edge = event
				edge.color = "yellow"
				last_edge = edge
			elif etype == "accept":
				_t, edge = event
				chosen.add(id(edge))
				edge.color = "yellow"
				last_edge = None

			self.app.draw_graph()
			i += 1
			if not self._can_schedule():
				self.app._anim_after_id = None
				return
			self.app._anim_after_id = self.app.after(delay_ms, step)

		step()

	def animate_kruskal(self, trace, mst_edges, delay_ms=500):
		self.cancel_animation()
		self.reset_visuals()
		self.app.draw_graph()

		chosen = set()
		last_edge = None
		i = 0

		def step():
			nonlocal i, last_edge

			if not self._can_schedule():
				self.app._anim_after_id = None
				return

			if i >= len(trace):
				self.app._anim_after_id = None
				self.reset_visuals()
				for e in mst_edges:
					e.color = "yellow"
				self.app.draw_graph()
				total = self._mst_total_weight(mst_edges)
				self.app.log(
					f"Kruskal: Hoàn thành. Cạnh={len(mst_edges)}, Tổng trọng số={total}",
					level='THÀNH CÔNG',
				)
				return

			if last_edge is not None and id(last_edge) not in chosen:
				last_edge.color = "gray70"
				last_edge = None

			event = trace[i]
			etype = event[0]
			_t, edge = event

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

			self.app.draw_graph()
			i += 1
			if not self._can_schedule():
				self.app._anim_after_id = None
				return
			self.app._anim_after_id = self.app.after(delay_ms, step)

		step()

	def animate_ford_fulkerson(self, trace, flow_network, max_flow, delay_ms=700):
		self.cancel_animation()
		self.reset_visuals()
		self.app.draw_graph()

		last_path_edges = []
		i = 0

		def step():
			nonlocal i, last_path_edges

			if not self._can_schedule():
				self.app._anim_after_id = None
				return

			if i >= len(trace):
				self.app._anim_after_id = None
				self.reset_visuals()
				for e in flow_network:
					if getattr(e, "flow", 0) > 0:
						e.color = "yellow"
				self.app.draw_graph()
				self.app.log(f"Ford-Fulkerson: Hoàn thành. luồng cực đại={max_flow}", level='THÀNH CÔNG')
				return

			for e in last_path_edges:
				e.color = "gray70"
			last_path_edges = []


			event = trace[i]
			etype = event[0]
			if etype == "augment":
				_t, path_pairs, bottleneck, flow_after = event
				self.app.log(f"Ford-Fulkerson: Tăng thêm +{bottleneck} (luồng={flow_after})", level='THÔNG BÁO')

				for (u, v) in path_pairs:
					for edge in self.app.edges:
						if int(edge.start_node.id) == int(u) and int(edge.end_node.id) == int(v):
							edge.color = "yellow"
							last_path_edges.append(edge)
							break

			self.app.draw_graph()
			i += 1
			if not self._can_schedule():
				self.app._anim_after_id = None
				return
			self.app._anim_after_id = self.app.after(delay_ms, step)

		step()

	# --------- public handlers (called by GraphApp) ---------

	def run_dijkstra(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Dijkstra: Không có đỉnh.", level='CẢNH BÁO')
			return

		start_id = simpledialog.askinteger("Dijkstra", "Start node id:")
		if start_id is None:
			return
		end_id = simpledialog.askinteger("Dijkstra", "End node id:")
		if end_id is None:
			return

		path, cost, trace = dijkstra_trace(self.app.nodes, self.app.edges, start_id, end_id)
		if not trace:
			path2, cost2 = dijkstra(self.app.nodes, self.app.edges, start_id, end_id)
			if not path2:
				self.reset_visuals()
				self.app.draw_graph()
				self.app.log(f"Dijkstra: Không tìm thấy đường đi từ {start_id} tới {end_id}.", level='CẢNH BÁO')
				return
			self._highlight_final_path(path2, cost2)
			return

		self.app.log(f"Dijkstra: Đang mô phỏng {len(trace)} bước...", level='THÔNG BÁO')
		self.animate_dijkstra(trace, path, cost, delay_ms=500)

	def run_prim(self):
		self.cancel_animation()
		if not self.app.nodes:
			self.app.log("Prim: Không có đỉnh.", level='CẢNH BÁO')
			return

		mst, trace = prim_trace(self.app.nodes, self.app.edges)
		if trace:
			self.app.log(f"Prim: Đang mô phỏng {len(trace)} bước...", level='THÔNG BÁO')
			self.animate_prim(trace, mst, delay_ms=500)
			return

		mst2 = prim(self.app.nodes, self.app.edges)
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

		mst, trace = kruskal_trace(self.app.nodes, self.app.edges)
		if trace:
			self.app.log(f"Kruskal: Đang mô phỏng {len(trace)} bước...", level='THÔNG BÁO')
			self.animate_kruskal(trace, mst, delay_ms=400)
			return

		mst2 = kruskal(self.app.nodes, self.app.edges)
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
		self.reset_visuals()
		self.app.draw_graph()
		
		node_map = {n.id: n for n in self.app.nodes}
		i = 0
		
		def step():
			nonlocal i
			if not self._can_schedule():
				self.app._anim_after_id = None
				return
			if i >= len(path_ids):
				self.app._anim_after_id = None
				self.app.log(f"{algo_name}: Hoàn thành.", level='THÀNH CÔNG')
				return
			
			node_id = path_ids[i]
			if node_id in node_map:
				node = node_map[node_id]
				node.color = "yellow"
				# Optional: Highlight edge from previous node if exists
				# Note: This is a simple visualization, it doesn't strictly follow the tree edges
				# but it shows the order of visitation.
			
			self.app.draw_graph()
			i += 1
			if not self._can_schedule():
				self.app._anim_after_id = None
				return
			self.app._anim_after_id = self.app.after(delay_ms, step)
			
		step()

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
		self.reset_visuals()
		self.app.draw_graph()
		
		node_map = {n.id: n for n in self.app.nodes}
		is_directed = bool(getattr(self.app, 'is_directed', False))
		# Map edges to support parallel edges and direction-aware lookup
		edge_map = {}
		for e in self.app.edges:
			u, v = int(e.start_node.id), int(e.end_node.id)
			if is_directed:
				edge_map.setdefault((u, v), []).append(e)
			else:
				key = frozenset((u, v))
				edge_map.setdefault(key, []).append(e)

		i = 0
		
		def step():
			nonlocal i
			if not self._can_schedule():
				self.app._anim_after_id = None
				return
			
			# Highlight start node
			if i == 0 and len(path_ids) > 0:
				if path_ids[0] in node_map:
					node_map[path_ids[0]].color = "yellow"

			# If we have visited at least one node, we can highlight the edge from prev to curr
			if i > 0 and i < len(path_ids):
				u_id = path_ids[i-1]
				v_id = path_ids[i]
				
				# Highlight node v
				if v_id in node_map:
					node_map[v_id].color = "yellow"
				
				# Highlight edge (u, v)
				key = (u_id, v_id) if is_directed else frozenset((u_id, v_id))
				lst = edge_map.get(key)
				if lst:
					ed = lst.pop(0)
					ed.color = "red"
			
			self.app.draw_graph()
			
			i += 1
			if i >= len(path_ids):
				self.app._anim_after_id = None
				self.app.log(f"{algo_name}: Hoàn thành.", level='THÀNH CÔNG')
				return

			if not self._can_schedule():
				self.app._anim_after_id = None
				return
			self.app._anim_after_id = self.app.after(delay_ms, step)
			
		step()

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
