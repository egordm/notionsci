import uuid
from time import sleep

from notion.client import NotionClient, Block

from notionsci.connections.notion import ID
from notionsci.connections.notion_unofficial.common import op_list_after_block, op_parent_block, op_user_permission, \
    op_copy_indicator


class NotionUnofficialClient(NotionClient):
    def get_task_status(self, task_id):
        """
        Get a status of a single task
        """
        data = self.post(
            "getTasks", {"taskIds": [task_id]}
        ).json()

        results = data.get("results")
        if results is None:
            return None

        if not results:
            # Notion does not know about such a task
            print("Invalid task ID.")
            return None

        if len(results) >= 1:
            return results[0].get("state")

        return None

    def wait_for_task(self, task_id, interval=1, tries=20):
        """
        Wait for a task by looping 'tries' times ever 'interval' seconds.
        The 'interval' parameter can be used to specify milliseconds using double (e.g 0.75).
        """
        for i in range(tries):
            state = self.get_task_status(task_id)
            if state in ["not_started", "in_progress"]:
                sleep(interval)
            elif state == "success":
                return state
            else:
                raise Exception('Unexpected task state: {}'.format(state))

        print("Task takes more time than expected. Specify 'interval' or 'tries' to wait more.")

    def submit_duplicate_task(self, source_id: ID, target_id: ID):
        """
        Submits a task to notion to duplicate a block to target'
        Target must have copy indicator and right permissions
        """
        data = self.post("enqueueTask", {
            "task": {
                "eventName": "duplicateBlock",
                "request": {
                    "sourceBlockId": source_id,
                    "targetBlockId": target_id,
                    "addCopyName": False,
                    "deepCopyTransclusionContainers": True,
                }
            }
        }).json()

        task_id = data.get("taskId")
        if task_id:
            # Wait until the duplication task finishes
            self.wait_for_task(task_id)

    def duplicate_page(self, source_id: ID, parent: Block):
        """
        Duplicates source page to a new child page of the given parent
        """
        block_id = str(uuid.uuid4())
        space_id = parent.space_info['spaceId']
        user_id = self.current_user.id
        parent_block_id = parent.id

        # Create a block with right copy indicator and user permission
        self.submit_transaction([
            op_copy_indicator(space_id, block_id),
            op_user_permission(block_id, user_id),
            op_parent_block(block_id, parent_block_id),
            op_list_after_block(block_id, parent_block_id)
        ])

        self.submit_duplicate_task(source_id, block_id)
