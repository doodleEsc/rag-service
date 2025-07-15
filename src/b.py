from tree_sitter import Language, Parser

import tree_sitter
from tree_sitter_language_pack import get_language, get_parser


parser = get_parser("go")

code_to_inspect = b"""
// Server aasdfasdfsaf
// asdfasf
type Server struct {
	listener net.Listener
	handler  Handler
	done     chan struct{}
}
"""

tree = parser.parse(code_to_inspect)
root_node = tree.root_node

# .sexp() 会以 S-表达式的格式打印出完整的语法树
# 这是调试查询语句的黄金标准！
print(root_node.sexp())
