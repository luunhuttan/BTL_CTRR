from __future__ import annotations

from tkinter import simpledialog

from algorithms.algo_opt import (
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


class AlgorithmRunner:
	"""Runs and animates algorithms step-by-step for a GraphApp instance."""

	def __init__(self, app):
		self.app = app

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

	def _highlight_final_path(self, path, cost):
		self.reset_visuals()

		path_nodes = set(path)
		for node in self.app.nodes:
			if int(node.id) in path_nodes:
				node.color = "yellow"

		path_pairs = set(zip(path, path[1:]))
		for edge in self.app.edges:
			u = int(edge.start_node.id)
			v = int(edge.end_node.id)
			if (u, v) in path_pairs:
				edge.color = "yellow"

		self.app.draw_graph()
		self.app.log(f"Dijkstra: Đường đi {path}, tổng chi phí={cost}", level='THÀNH CÔNG')

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

			if i >= len(trace):
				self.app._anim_after_id = None
				self.reset_visuals()
				for e in mst_edges:
					e.color = "yellow"
				self.app.draw_graph()
				self.app.log(f"Prim: Hoàn thành. Cạnh={len(mst_edges)}", level='THÀNH CÔNG')
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

			if i >= len(trace):
				self.app._anim_after_id = None
				self.reset_visuals()
				for e in mst_edges:
					e.color = "yellow"
				self.app.draw_graph()
				self.app.log(f"Kruskal: Hoàn thành. Cạnh={len(mst_edges)}", level='THÀNH CÔNG')
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
		self.app.log(f"Prim: Hoàn thành. Cạnh={len(mst2)}", level='THÀNH CÔNG')

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
		self.app.log(f"Kruskal: Hoàn thành. Cạnh={len(mst2)}", level='THÀNH CÔNG')

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

		self.app.log(f"DFS: Đã thăm {len(path)} đỉnh. Đang mô phỏng...", level='THÔNG BÁO')
		self.animate_traversal(path, "DFS")

	def animate_traversal(self, path_ids, algo_name, delay_ms=500):
		self.reset_visuals()
		self.app.draw_graph()
		
		node_map = {n.id: n for n in self.app.nodes}
		i = 0
		
		def step():
			nonlocal i
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
