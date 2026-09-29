import React from 'react';

const SourceTagBadge = ({ sourceTag, size = 'small' }) => {
  const getTagStyle = (tag) => {
    const styles = {
      'REAL_OFFICIAL': { bg: '#10b981', text: 'Official MOIL Data' },
      'REAL_PUBLIC': { bg: '#3b82f6', text: 'Public Data' },
      'PROXY': { bg: '#f59e0b', text: 'Proxy Data' },
      'SYNTHETIC': { bg: '#ef4444', text: 'Synthetic Data' },
    };
    return styles[tag] || { bg: '#6b7280', text: tag };
  };

  const style = getTagStyle(sourceTag);
  const sizeClass = size === 'large' ? 'badge-large' : 'badge-small';

  return (
    <span 
      className={`source-tag-badge ${sizeClass}`}
      style={{ backgroundColor: style.bg }}
      title={style.text}
    >
      {sourceTag}
    </span>
  );
};

export default SourceTagBadge;
