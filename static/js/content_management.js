/**
 * Content Management JavaScript
 * Handles AJAX operations for content CRUD operations
 */

// Global variables
let currentContentId = null;
let contentTable = null;
let selectedItems = new Set();
let currentBulkAction = null;

// Get CSRF token from the form
function getCSRFToken() {
    return document.querySelector('[name=csrf_token]').value;
}

$(document).ready(function() {
    // Setup AJAX defaults to include CSRF token
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
            }
        }
    });
    
    // Load content list on page load
    loadContentList();
    
    // Initialize event handlers
    initializeEventHandlers();
});

function loadContentList(filters = {}) {
    // Properly destroy existing DataTable
    if ($.fn.DataTable.isDataTable('#contentTable')) {
        $('#contentTable').DataTable().clear().destroy();
        $('#contentTable').empty();
    }
    
    const params = new URLSearchParams(filters).toString();
    const url = '/content/list' + (params ? '?' + params : '');
    
    // Clear selection when loading new content
    selectedItems.clear();
    updateBulkActionsBar();
    
    $.get(url)
        .done(function(response) {
            $('#contentTable').html(response.html);
            // Small delay to ensure DOM is ready
            setTimeout(() => {
                initializeDataTable();
                initializeBulkActions();
            }, 100);
        })
        .fail(function(xhr) {
            showAlert('error', 'Failed to load content list: ' + xhr.responseJSON?.error || 'Unknown error');
        });
}

function initializeDataTable() {
    // Ensure table exists before initializing
    if ($('#contentTable').length === 0) {
        return;
    }
    
    // Check if table has proper structure (thead and tbody)
    const $table = $('#contentTable');
    const $thead = $table.find('thead');
    const $tbody = $table.find('tbody');
    
    if ($thead.length === 0 || $thead.find('tr th').length === 0) {
        return;
    }
    
    // Validate table structure integrity
    const headerColumnCount = $thead.find('tr:first th').length;
    const hasValidStructure = headerColumnCount > 0;
    
    if (!hasValidStructure) {
        return;
    }
    
    // Check if tbody exists, if not create it
    if ($tbody.length === 0) {
        $table.append('<tbody></tbody>');
        $tbody = $table.find('tbody'); // Update reference
    }
    
    // Handle empty table case - add a temporary row to prevent DataTables errors
    let $dataRows = $tbody.find('tr');
    let addedPlaceholderRow = false;
    
    if ($dataRows.length === 0) {
        // Add a hidden placeholder row with correct number of cells
        let placeholderCells = '';
        for (let i = 0; i < headerColumnCount; i++) {
            placeholderCells += '<td></td>';
        }
        $tbody.append(`<tr id="placeholder-row" style="display: none;">${placeholderCells}</tr>`);
        addedPlaceholderRow = true;
        $dataRows = $tbody.find('tr'); // Update reference
    }
    
    // Validate row structure if data rows exist
    if ($dataRows.length > 0) {
        const visibleRows = $dataRows.filter(':visible');
        if (visibleRows.length > 0) {
            const firstRowCellCount = visibleRows.first().find('td').length;
            if (firstRowCellCount !== headerColumnCount) {
                // Don't return, let DataTables handle it
            }
        }
    }
    
    try {
        // Use a more conservative column configuration
        const columnCount = headerColumnCount;
        
        let columnDefs = [];
        let orderColumn = Math.min(5, columnCount - 1); // Safe order column
        
        // More conservative column definitions
        if (columnCount >= 7) {
            columnDefs = [
                { orderable: false, targets: [0] }, // Checkbox column
                { orderable: false, targets: [columnCount - 1] }, // Actions column (last)
                { visible: false, targets: [columnCount - 2, columnCount - 3] }, // Hidden columns (last two)
                { searchable: false, targets: [0, columnCount - 1, columnCount - 2, columnCount - 3] }
            ];
            orderColumn = 5; // Date created column
        } else if (columnCount > 2) {
            columnDefs = [
                { orderable: false, targets: [columnCount - 1] } // Last column
            ];
            orderColumn = Math.max(1, columnCount - 2);
        }
        
        // Ensure order column is valid
        if (orderColumn >= columnCount) {
            orderColumn = Math.max(0, columnCount - 1);
        }
        
        contentTable = $('#contentTable').DataTable({
            order: [[orderColumn, 'desc']],
            pageLength: 25,
            responsive: true,
            columnDefs: columnDefs,
            autoWidth: false,
            processing: false,
            language: {
                lengthMenu: "Show _MENU_ contents per page",
                zeroRecords: "No matching contents found",
                info: "Showing _START_ to _END_ of _TOTAL_ contents",
                infoEmpty: "No contents available",
                infoFiltered: "(filtered from _MAX_ total contents)"
            },
            dom: "<'row'<'col-sm-12'l>>" +
                "<'row'<'col-sm-12'tr>>" +
                "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            drawCallback: function() {
                // Re-initialize bulk action event handlers after table redraw
                try {
                    initializeBulkActions();
                } catch (e) {
                    // Silently handle error
                }
            }
        });
        
        // Remove placeholder row if it was added
        if (addedPlaceholderRow) {
            setTimeout(() => {
                $('#placeholder-row').remove();
            }, 100);
        }
        
    } catch (error) {
        // Clean up placeholder row on error
        if (addedPlaceholderRow) {
            $('#placeholder-row').remove();
        }
    }
}

function initializeEventHandlers() {
    // Add content form submission
    $('#addContentForm').on('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        data.is_active = $('#add_is_active').is(':checked');
        
        $.ajax({
            url: '/content/add',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            headers: {
                'X-CSRFToken': data.csrf_token
            },
            success: function(response) {
                if (response.success) {
                    showAlert('success', 'Content created successfully!');
                    $('#addContentModal').modal('hide');
                    $('#addContentForm')[0].reset();
                    loadContentList();
                } else {
                    showAlert('error', response.error || 'Failed to create content');
                }
            },
            error: function(xhr) {
                showAlert('error', xhr.responseJSON?.error || 'Failed to create content');
            }
        });
    });
    
    // Edit content form submission
    $('#editContentForm').on('submit', function(e) {
        e.preventDefault();
        const contentId = $('#edit_content_id').val();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        data.is_active = $('#edit_is_active').is(':checked');
        
        $.ajax({
            url: `/content/edit/${contentId}`,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            headers: {
                'X-CSRFToken': data.csrf_token
            },
            success: function(response) {
                if (response.success) {
                    showAlert('success', 'Content updated successfully!');
                    $('#editContentModal').modal('hide');
                    loadContentList();
                } else {
                    showAlert('error', response.error || 'Failed to update content');
                }
            },
            error: function(xhr) {
                showAlert('error', xhr.responseJSON?.error || 'Failed to update content');
            }
        });
    });
    
    // Delete confirmation
    $('#confirmDeleteBtn').on('click', function() {
        if (currentContentId) {
            $.ajax({
                url: `/content/delete/${currentContentId}`,
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                },
                success: function(response) {
                    if (response.success) {
                        showAlert('success', 'Content deleted successfully!');
                        $('#deleteContentModal').modal('hide');
                        loadContentList();
                    } else {
                        showAlert('error', response.error || 'Failed to delete content');
                    }
                },
                error: function(xhr) {
                    showAlert('error', xhr.responseJSON?.error || 'Failed to delete content');
                }
            });
        }
    });
    
    // Filter options - use event delegation to ensure it works after page loads
    $(document).on('click', '.filter-option', function(e) {
        e.preventDefault();
        const filter = $(this).data('filter');
        const filterText = $(this).text();
        
        // Update filter button text to show active filter
        $('#filterDropdown').html(`<i class="fas fa-filter"></i> ${filterText}`);
        
        // Remove active class from all filter options and add to current
        $('.filter-option').removeClass('active');
        $(this).addClass('active');
        
        applyFilter(filter);
    });
    
    // Search functionality
    $('#searchInput').on('keypress', function(e) {
        if (e.which === 13) {
            searchContent();
        }
    });
    
    // Event delegation for dynamic content
    $(document).on('click', '.view-content', function() {
        const contentId = $(this).data('content-id');
        viewContent(contentId);
    });
    
    $(document).on('click', '.edit-content', function() {
        const contentId = $(this).data('content-id');
        editContent(contentId);
    });
    
    $(document).on('click', '.delete-content', function() {
        const contentId = $(this).data('content-id');
        const contentPreview = $(this).closest('tr').find('td:nth-child(3)').text().substring(0, 100) + '...';
        showDeleteConfirmation(contentId, contentPreview);
    });
    
    $(document).on('click', '.toggle-status', function() {
        const contentId = $(this).data('content-id');
        toggleContentStatus(contentId);
    });
}

function viewContent(contentId) {
    $.get(`/content/${contentId}?format=json`)
        .done(function(response) {
            if (response.success) {
                const content = response.data;
                currentContentId = contentId;
                
                $('#view_author').text(content.author || 'N/A');
                $('#view_content_type').text(formatContentType(content.content_type) || 'N/A');
                $('#view_category').text(formatCategory(content.category) || 'N/A');
                $('#view_target_audience').text(formatTargetAudience(content.target_audience) || 'N/A');
                $('#view_messages').html(content.messages || 'N/A');
                $('#view_tags').text(content.tags || 'No tags');
                
                const statusBadge = content.is_active ? 
                    '<span class="badge bg-success">Active</span>' : 
                    '<span class="badge bg-secondary">Inactive</span>';
                $('#view_status').html(statusBadge);
                
                $('#view_created_at').text(formatDateTime(content.created_at));
                $('#view_updated_at').text(formatDateTime(content.updated_at));
                $('#view_created_by').text(content.created_by || 'N/A');
                
                $('#viewContentModal').modal('show');
            } else {
                showAlert('error', response.error || 'Failed to load content');
            }
        })
        .fail(function(xhr) {
            showAlert('error', xhr.responseJSON?.error || 'Failed to load content');
        });
}

function editContent(contentId) {
    $.get(`/content/${contentId}?format=json`)
        .done(function(response) {
            if (response.success) {
                const content = response.data;
                
                $('#edit_content_id').val(content.id);
                $('#edit_author').val(content.author);
                $('#edit_content_type').val(content.content_type);
                $('#edit_category').val(content.category);
                $('#edit_target_audience').val(content.target_audience);
                $('#edit_messages').val(content.messages);
                $('#edit_tags').val(content.tags);
                $('#edit_is_active').prop('checked', content.is_active);
                
                $('#editContentModal').modal('show');
            } else {
                showAlert('error', response.error || 'Failed to load content for editing');
            }
        })
        .fail(function(xhr) {
            showAlert('error', xhr.responseJSON?.error || 'Failed to load content for editing');
        });
}

function editContentFromView() {
    $('#viewContentModal').modal('hide');
    setTimeout(() => {
        editContent(currentContentId);
    }, 300);
}

function showDeleteConfirmation(contentId, contentPreview) {
    currentContentId = contentId;
    $('#delete_content_preview').text(contentPreview);
    $('#deleteContentModal').modal('show');
}

function toggleContentStatus(contentId) {
    $.ajax({
        url: `/content/toggle-status/${contentId}`,
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        success: function(response) {
            if (response.success) {
                showAlert('success', response.message);
                loadContentList();
            } else {
                showAlert('error', response.error || 'Failed to update status');
            }
        },
        error: function(xhr) {
            showAlert('error', xhr.responseJSON?.error || 'Failed to update status');
        }
    });
}

function searchContent() {
    const query = $('#searchInput').val().trim();
    if (query) {
        // Clear selection when searching
        selectedItems.clear();
        updateBulkActionsBar();
        
        // Properly destroy existing DataTable
        if ($.fn.DataTable.isDataTable('#contentTable')) {
            $('#contentTable').DataTable().clear().destroy();
            $('#contentTable').empty();
        }
        
        $.get(`/content/search?q=${encodeURIComponent(query)}`)
            .done(function(response) {
                $('#contentTable').html(response.html);
                // Small delay to ensure DOM is ready
                setTimeout(() => {
                    initializeDataTable();
                    initializeBulkActions();
                }, 100);
            })
            .fail(function(xhr) {
                showAlert('error', 'Search failed: ' + (xhr.responseJSON?.error || 'Unknown error'));
            });
    } else {
        loadContentList();
    }
}

function applyFilter(filter) {
    // Clear selection when applying filters
    selectedItems.clear();
    updateBulkActionsBar();
    
    // If DataTable is initialized, use client-side filtering for immediate response
    if ($.fn.DataTable.isDataTable('#contentTable')) {
        const table = $('#contentTable').DataTable();
        
        // Clear any existing search
        table.search('').draw();
        
        // Remove any existing custom search functions
        $.fn.dataTable.ext.search = [];
        
        // Apply custom filter based on hidden columns
        if (filter && filter !== 'all') {
            $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
                // data array contains all column values
                // Column 7 (index 7): hidden_status
                // Column 8 (index 8): hidden_contenttype
                
                // Handle null/undefined values by defaulting to appropriate values
                const status = data[7] || 'inactive';
                const contentType = data[8] || 'general';
                
                switch(filter) {
                    case 'active':
                        return status === 'active'; // hidden_status column
                    case 'inactive':
                        return status === 'inactive'; // hidden_status column
                    case 'general':
                    case 'mental_health':
                    case 'educational':
                    case 'motivational':
                    case 'awareness':
                    case 'announcement':
                        return contentType === filter; // hidden_contenttype column
                    default:
                        return true;
                }
            });
        }
        
        // Redraw table with filter applied
        table.draw();
        
    } else {
        // Fall back to server-side filtering if DataTable not initialized
        let filters = {};
        
        switch(filter) {
            case 'active':
                filters.status = 'active';
                break;
            case 'inactive':
                filters.status = 'inactive';
                break;
            case 'general':
            case 'mental_health':
            case 'educational':
            case 'motivational':
            case 'awareness':
            case 'announcement':
                filters.content_type = filter;
                break;
            case 'all':
            default:
                filters = {};
                break;
        }
        
        loadContentList(filters);
    }
}

function refreshContentList() {
    // Clear search input
    if ($('#searchInput').length) {
        $('#searchInput').val('');
    }
    
    // Reset filter display
    $('#filterDropdown').html('<i class="fas fa-filter"></i> Filter');
    $('.filter-option').removeClass('active');
    
    // Clear custom DataTable search functions
    $.fn.dataTable.ext.search = [];
    
    // Properly destroy existing DataTable
    if ($.fn.DataTable.isDataTable('#contentTable')) {
        $('#contentTable').DataTable().clear().destroy();
        $('#contentTable').empty();
    }
    
    // Clear selection
    selectedItems.clear();
    updateBulkActionsBar();
    
    // Reload content list
    loadContentList();
    showAlert('info', 'Content list refreshed');
}

// Utility functions
function formatContentType(type) {
    const types = {
        'general': 'General',
        'mental_health': 'Mental Health',
        'educational': 'Educational',
        'motivational': 'Motivational',
        'awareness': 'Awareness',
        'announcement': 'Announcement'
    };
    return types[type] || type;
}

function formatCategory(category) {
    const categories = {
        'student_support': 'Student Support',
        'wellness': 'Wellness',
        'academic': 'Academic',
        'social': 'Social',
        'career': 'Career',
        'health': 'Health',
        'emergency': 'Emergency'
    };
    return categories[category] || category;
}

function formatTargetAudience(audience) {
    const audiences = {
        'all_students': 'All Students',
        'freshmen': 'Freshmen',
        'sophomores': 'Sophomores',
        'juniors': 'Juniors',
        'seniors': 'Seniors',
        'graduate_students': 'Graduate Students',
        'staff': 'Staff',
        'faculty': 'Faculty'
    };
    return audiences[audience] || audience;
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    try {
        return new Date(dateString).toLocaleString();
    } catch (e) {
        return dateString;
    }
}

function showAlert(type, message) {
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-danger' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const alert = $(`
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('.container-fluid').prepend(alert);
    
    setTimeout(() => {
        alert.fadeOut();
    }, 5000);
}

// Make functions globally available
window.refreshContentList = refreshContentList;
window.searchContent = searchContent;
window.editContentFromView = editContentFromView;

// Bulk Actions Functions
function initializeBulkActions() {
    // Master checkbox handler
    $(document).off('change', '#selectAll').on('change', '#selectAll', function() {
        const isChecked = $(this).is(':checked');
        $('.item-checkbox').prop('checked', isChecked);
        if (isChecked) {
            $('.item-checkbox').each(function() {
                selectedItems.add($(this).val());
            });
        } else {
            selectedItems.clear();
        }
        updateBulkActionsBar();
    });

    // Individual checkbox handler
    $(document).off('change', '.item-checkbox').on('change', '.item-checkbox', function() {
        const contentId = $(this).val();
        if ($(this).is(':checked')) {
            selectedItems.add(contentId);
        } else {
            selectedItems.delete(contentId);
        }
        
        // Update master checkbox state
        const totalCheckboxes = $('.item-checkbox').length;
        const checkedCheckboxes = $('.item-checkbox:checked').length;
        
        $('#selectAll').prop('checked', checkedCheckboxes === totalCheckboxes && totalCheckboxes > 0);
        $('#selectAll').prop('indeterminate', checkedCheckboxes > 0 && checkedCheckboxes < totalCheckboxes);
        
        updateBulkActionsBar();
    });
}

function updateBulkActionsBar() {
    const selectedCount = selectedItems.size;
    $('#selectedCount').text(selectedCount);
    
    if (selectedCount > 0) {
        $('#bulkActionsBar').slideDown(200);
    } else {
        $('#bulkActionsBar').slideUp(200);
    }
}

function clearSelection() {
    selectedItems.clear();
    $('.item-checkbox, #selectAll').prop('checked', false);
    $('#selectAll').prop('indeterminate', false);
    updateBulkActionsBar();
}

function bulkActivate() {
    if (selectedItems.size === 0) {
        showAlert('warning', 'Please select items to activate');
        return;
    }
    
    currentBulkAction = 'activate';
    $('#bulkActionModalLabel').html('<i class="fas fa-check-circle me-2 text-success"></i>Confirm Bulk Activation');
    $('#bulkActionMessage').text('Are you sure you want to activate the selected content items?');
    $('#bulkActionCount').text(selectedItems.size);
    $('#bulkActionWarning').hide();
    $('#confirmBulkActionBtn').removeClass('btn-danger btn-warning').addClass('btn-success').html('<i class="fas fa-check me-1"></i>Activate');
    $('#bulkActionModal').modal('show');
}

function bulkDeactivate() {
    if (selectedItems.size === 0) {
        showAlert('warning', 'Please select items to deactivate');
        return;
    }
    
    currentBulkAction = 'deactivate';
    $('#bulkActionModalLabel').html('<i class="fas fa-pause-circle me-2 text-warning"></i>Confirm Bulk Deactivation');
    $('#bulkActionMessage').text('Are you sure you want to deactivate the selected content items?');
    $('#bulkActionCount').text(selectedItems.size);
    $('#bulkActionWarning').hide();
    $('#confirmBulkActionBtn').removeClass('btn-danger btn-success').addClass('btn-warning').html('<i class="fas fa-pause me-1"></i>Deactivate');
    $('#bulkActionModal').modal('show');
}

function bulkDelete() {
    if (selectedItems.size === 0) {
        showAlert('warning', 'Please select items to delete');
        return;
    }
    
    currentBulkAction = 'delete';
    $('#bulkActionModalLabel').html('<i class="fas fa-trash me-2 text-danger"></i>Confirm Bulk Deletion');
    $('#bulkActionMessage').text('Are you sure you want to permanently delete the selected content items?');
    $('#bulkActionCount').text(selectedItems.size);
    $('#bulkActionWarning').show();
    $('#confirmBulkActionBtn').removeClass('btn-success btn-warning').addClass('btn-danger').html('<i class="fas fa-trash me-1"></i>Delete');
    $('#bulkActionModal').modal('show');
}

function executeBulkAction() {
    if (!currentBulkAction || selectedItems.size === 0) {
        return;
    }
    
    const itemsArray = Array.from(selectedItems);
    let endpoint, method, data;
    
    switch (currentBulkAction) {
        case 'activate':
            endpoint = '/content/bulk-activate';
            method = 'POST';
            data = { content_ids: itemsArray };
            break;
        case 'deactivate':
            endpoint = '/content/bulk-deactivate';
            method = 'POST';
            data = { content_ids: itemsArray };
            break;
        case 'delete':
            endpoint = '/content/bulk-delete';
            method = 'DELETE';
            data = { content_ids: itemsArray };
            break;
        default:
            return;
    }
    
    // Show loading state
    $('#confirmBulkActionBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i>Processing...');
    
    $.ajax({
        url: endpoint,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(data),
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        success: function(response) {
            if (response.success) {
                showAlert('success', response.message || `${currentBulkAction} completed successfully!`);
                $('#bulkActionModal').modal('hide');
                clearSelection();
                loadContentList();
            } else {
                showAlert('error', response.error || `Failed to ${currentBulkAction} selected items`);
            }
        },
        error: function(xhr) {
            showAlert('error', xhr.responseJSON?.error || `Failed to ${currentBulkAction} selected items`);
        },
        complete: function() {
            $('#confirmBulkActionBtn').prop('disabled', false);
            currentBulkAction = null;
        }
    });
}

// Initialize bulk action confirmation handler
$(document).ready(function() {
    $('#confirmBulkActionBtn').on('click', executeBulkAction);
});

// Export bulk action functions for global access
window.bulkActivate = bulkActivate;
window.bulkDeactivate = bulkDeactivate;
window.bulkDelete = bulkDelete;
window.clearSelection = clearSelection;