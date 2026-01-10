import React from 'react';
import { Group, Tooltip, ActionIcon, Divider, Modal, Stack, Text, Button } from '@mantine/core';
import { Link } from 'react-router-dom';

interface ToolActionsProps {
  connectedTools: any[];
  syncingTools: Set<string>;
  handleToolSync: (toolId: string, toolName: string) => void;
  setDeleteModal: (v: { open: boolean; deleting: boolean }) => void;
  deleteModal: { open: boolean; deleting: boolean };
  handleDelete: () => void;
  saveState: any;
  handleSave: () => void;
  isDark: boolean;
}

const ToolActions: React.FC<ToolActionsProps> = ({ connectedTools, syncingTools, handleToolSync, setDeleteModal, deleteModal, handleDelete, saveState, handleSave, isDark }) => (
  <Group gap="sm">
    {connectedTools.map((tool) => (
      <Tooltip key={tool.id} label={`Sync to ${tool.name}`}>
        <ActionIcon
          variant="light"
          color={tool.color}
          size="lg"
          radius="md"
          loading={syncingTools.has(tool.id)}
          onClick={() => handleToolSync(tool.id, tool.name)}
        >
          <i className={tool.icon}></i>
        </ActionIcon>
      </Tooltip>
    ))}

    {connectedTools.length === 0 && (
      <Tooltip label="Connect Tools">
        <ActionIcon
          variant="light"
          color="indigo"
          size="lg"
          radius="md"
          component={Link}
          to="/tools"
        >
          <i className="fas fa-plug"></i>
        </ActionIcon>
      </Tooltip>
    )}

    <Divider orientation="vertical" />

    <Tooltip label="Delete Analysis">
      <ActionIcon
        variant="light"
        color="red"
        size="lg"
        radius="md"
        onClick={() => setDeleteModal({ open: true, deleting: false })}
      >
        <i className="fas fa-trash-alt"></i>
      </ActionIcon>
    </Tooltip>

    <Modal
      opened={deleteModal.open}
      onClose={() => setDeleteModal({ open: false, deleting: false })}
      title="Delete Video Analysis?"
      centered
      withCloseButton={!deleteModal.deleting}
      closeOnClickOutside={!deleteModal.deleting}
      closeOnEscape={!deleteModal.deleting}
    >
      <Stack gap="md">
        <Text>Are you sure you want to delete this video analysis? This action cannot be undone.</Text>
        <Group justify="flex-end">
          <Button variant="default" onClick={() => setDeleteModal({ open: false, deleting: false })} disabled={deleteModal.deleting}>
            Cancel
          </Button>
          <Button color="red" loading={deleteModal.deleting} onClick={handleDelete}>
            Delete
          </Button>
        </Group>
      </Stack>
    </Modal>

    <Tooltip label="Save to Library">
      <ActionIcon
        variant="light"
        color={saveState.saveSuccess ? 'green' : 'gray'}
        size="lg"
        radius="md"
        onClick={handleSave}
        loading={saveState.saving}
      >
        <i className={saveState.saveSuccess ? "fas fa-bookmark" : "far fa-bookmark"}></i>
      </ActionIcon>
    </Tooltip>
    {saveState.saveError && <Text color="red" size="xs">{saveState.saveError}</Text>}
  </Group>
);

export default ToolActions;