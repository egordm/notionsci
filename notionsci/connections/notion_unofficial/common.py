from notion.operations import build_operation

from notionsci.connections.notion import ID


def op_copy_indicator(space_id: ID, block_id: ID):
    return build_operation(
        id=block_id, table="block",
        path=[], command="set",
        args={
            "type": "copy_indicator",
            "space_id": space_id,
            "id": block_id,
            "version": 1
        },
    )


def op_user_permission(block_id: ID, user_id: ID):
    return build_operation(
        id=block_id, table="block",
        path=[], command="update",
        args={
            "permissions": [{
                "type": "user_permission",
                "role": "editor",
                "user_id": user_id
            }]
        }
    )


def op_parent_block(block_id: ID, parent_block_id: ID):
    return build_operation(
        id=block_id, table="block",
        path=[], command="update",
        args={
            "parent_id": parent_block_id,
            "parent_table": "block",
            "alive": True
        }
    )


def op_list_after_block(block_id: ID, parent_block_id: ID):
    return build_operation(
        id=parent_block_id, table="block",
        path=["content"], command="listAfter",
        args={
            "id": block_id,
        }
    )
