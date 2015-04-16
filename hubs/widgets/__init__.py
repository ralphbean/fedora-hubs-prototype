import dummy
import stats
import rules
import sticky

registry = {
    'dummy': dummy.render,
    'stats': stats.render,
    'rules': rules.render,
    'sticky': sticky.render,
}
