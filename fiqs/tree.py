RESERVED_KEYS = frozenset({
    "key",
    "key_as_string",
    "doc_count",
    "from",
    "from_as_string",
    "to",
    "to_as_string",
})


class ResultTree:
    def __init__(self, es_result):
        if isinstance(es_result, dict):
            self.es_result = es_result
        elif hasattr(es_result, "_d_"):
            self.es_result = es_result._d_
        else:
            raise Exception(
                "ResultTree expects a dict or " "an elasticsearch.dsl Response object"
            )

    def flatten_result(self, **kwargs):
        if "aggregations" not in self.es_result:
            return []

        self.add_others_line = kwargs.get("add_others_line", False)
        self.remove_nested_aggregations = kwargs.get("remove_nested_aggregations", True)

        aggregations = self.es_result["aggregations"]
        return self._extract_lines(aggregations)

    def _is_nested_node(self, node, parent_is_root=True, same_level_keys=None):
        # Not even a node, or a list of buckets
        if not isinstance(node, dict):
            return False

        # Standard aggregation
        if "buckets" in node:
            return False

        # Bucket
        if "key" in node:
            return False

        # Range bucket
        if "from" in node or "to" in node:
            return False

        # Nested nodes have a doc_count
        if "doc_count" not in node:
            return False

        # Can happen with filters aggregations
        if same_level_keys is not None:
            if not parent_is_root and "doc_count" not in same_level_keys:
                return False

        child_keys = node.keys()
        for child_node in node.values():
            if not isinstance(child_node, dict):
                continue
            is_nested_child_node = self._is_nested_node(
                child_node,
                parent_is_root=False,
                same_level_keys=child_keys,
            )
            if "doc_count" in child_node and not is_nested_child_node:
                return False

        # Node like {'value': 123.456}
        if all(not isinstance(child_node, dict) for child_node in node.values()):
            return False

        return True

    def _remove_nested_aggregations(self, node, parent_is_root=True):
        _node = {}

        # We force an ordering to have a deterministic result
        child_keys = sorted(node.keys(), reverse=True)
        child_keys_set = frozenset(node.keys())
        for key in child_keys:
            child_node = node[key]

            if key.startswith("reverse_nested"):
                _node[key] = child_node

            elif isinstance(child_node, dict):
                if self._is_nested_node(child_node, parent_is_root, child_keys_set):
                    _node.update(
                        self._remove_nested_aggregations(
                            child_node,
                            parent_is_root=False,
                        )
                    )
                else:
                    _node[key] = self._remove_nested_aggregations(
                        child_node,
                        parent_is_root=False,
                    )

            elif isinstance(child_node, list):
                _node[key] = [
                    self._remove_nested_aggregations(
                        gchild_node,
                        parent_is_root=False,
                    )
                    if isinstance(gchild_node, dict)
                    else gchild_node
                    for gchild_node in child_node
                ]

            else:
                _node[key] = child_node

        return _node

    def _create_line(self, base_line, node):
        new_line = base_line.copy()

        for k, v in node.items():
            if k.startswith("reverse_nested"):
                for nested_k, nested_v in v.items():
                    if isinstance(nested_v, dict):
                        value = nested_v["value"]
                    else:
                        value = nested_v
                    new_line[f"{k}__{nested_k}"] = value

            elif k == "doc_count":
                new_line[k] = v
            elif k in RESERVED_KEYS:
                continue
            elif isinstance(v, dict) and "value" in v:
                new_line[k] = v["value"]

        return new_line

    def _create_others_line(self, base_line, key, others_doc_count):
        new_line = base_line.copy()

        new_line[key] = "others"
        new_line["doc_count"] = others_doc_count

        return new_line

    def _bootstrap_current_key(self, aggregations):
        return min(k for k in aggregations if k not in RESERVED_KEYS)

    def _extract_lines(self, aggregations):
        current_key = self._bootstrap_current_key(aggregations)
        node = aggregations[current_key]

        # Are we dealing with a metric without aggs?
        if "buckets" not in node and "doc_count" not in node:
            return [{key: aggregations[key]["value"] for key in aggregations}]

        if self.remove_nested_aggregations:
            # We remove nested aggregations, I don't see the point
            # of exposing them and they are annoying to deal with
            aggregations = self._remove_nested_aggregations(aggregations)

        # The smallest top-level aggregation key first, then the others in order
        first_key = self._bootstrap_current_key(aggregations)
        keys = [first_key] + [
            k for k in aggregations if k not in RESERVED_KEYS and k != first_key
        ]

        lines = []
        for key in keys:
            self._extract_agg_lines(aggregations[key], key, {}, lines)
        return lines

    @staticmethod
    def _has_buckets(node):
        return isinstance(node, dict) and "buckets" in node

    def _extract_agg_lines(self, node, key, base_line, lines):
        """Append to `lines` one line per leaf bucket of the aggregation `node`."""
        if self.add_others_line and "sum_other_doc_count" in node:
            lines.append(
                self._create_others_line(base_line, key, node["sum_other_doc_count"])
            )

        buckets = node["buckets"]
        if isinstance(buckets, dict):
            # Keyed buckets (filters, keyed ranges), sorted by key
            buckets = [{**bucket, "key": k} for k, bucket in sorted(buckets.items())]

        for bucket in buckets:
            bucket_line = {**base_line, key: bucket["key"]}
            sub_keys = [k for k in bucket if k not in RESERVED_KEYS]
            # A bucket whose first sub-aggregation has buckets is not a leaf: its
            # sub-aggregations are flattened in turn
            if sub_keys and self._has_buckets(bucket[sub_keys[0]]):
                for sub_key in sub_keys:
                    if self._has_buckets(bucket[sub_key]):
                        self._extract_agg_lines(
                            bucket[sub_key], sub_key, bucket_line, lines
                        )
            else:
                lines.append(self._create_line(bucket_line, bucket))
